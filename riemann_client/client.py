"""Clients manage the main user facing API, and provide functions for sending
events and querying the Riemann server. UDP, TCP and TLS transports are
provided by the :py:mod:`riemann_client.transport` module, and the protocol
buffer objects are provided by the :py:mod:`riemann_client.riemann_pb2` module.
"""

from __future__ import absolute_import

import logging
try:
    from logging import NullHandler
except ImportError:
    # Create a NullHandler class in logging for python 2.6
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

import socket
try:
    from threading import RLock
    from threading import Timer
except ImportError:
    RLock = None
    Timer = None
import time

import riemann_client.riemann_pb2
import riemann_client.transport

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())


class Client(object):
    """A client for sending events and querying a Riemann server.

    Two sets of methods are provided - an API dealing directly with protocol
    buffer objects and an extended API that takes and returns dictionaries
    representing events.

    Protocol buffer API:

        - :py:meth:`.send_event`
        - :py:meth:`.send_events`
        - :py:meth:`.send_query`

    Extended API:

        - :py:meth:`.event`
        - :py:meth:`.events`
        - :py:meth:`.query`

    Clients do not directly manage connections to a Riemann server - these are
    managed by :py:class:`riemann_client.transport.Transport` instances, which
    provide methods to read and write messages to the server. Client instances
    can be used as a context manager, and will connect and disconnect the
    transport when entering and exiting the context.

        >>> with Client(transport) as client:
        ...     # Calls transport.connect()
        ...     client.query('true')
        ...     # Calls transport.disconnect()
    """

    def __init__(self, transport=None):
        if transport is None:
            transport = riemann_client.transport.TCPTransport()
        self.transport = transport

    def __enter__(self):
        self.transport.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.transport.disconnect()

    @staticmethod
    def create_event(data):
        """Translates a dictionary of event attributes to an Event object

        :param dict data: The attributes to be set on the event
        :returns: A protocol buffer ``Event`` object
        """
        event = riemann_client.riemann_pb2.Event()
        event.host = socket.gethostname()
        event.tags.extend(data.pop('tags', []))

        for key, value in data.pop('attributes', {}).items():
            attribute = event.attributes.add()
            attribute.key, attribute.value = key, value

        for name, value in data.items():
            if value is not None:
                setattr(event, name, value)
        return event

    def send_events(self, events):
        """Sends multiple events to Riemann in a single message

        :param events: A list or iterable of ``Event`` objects
        :returns: The response message from Riemann
        """
        message = riemann_client.riemann_pb2.Msg()
        for event in events:
            message.events.add().MergeFrom(event)
        return self.transport.send(message)

    def send_event(self, event):
        """Sends a single event to Riemann

        :param event: An ``Event`` protocol buffer object
        :returns: The response message from Riemann
        """
        return self.send_events((event,))

    def events(self, *events):
        """Sends multiple events in a single message

        >>> client.events({'service': 'riemann-client', 'state': 'awesome'})

         :param \*events: event dictionaries for :py:func:`create_event`
         :returns: The response message from Riemann
        """
        return self.send_events(self.create_event(e) for e in events)

    def event(self, **data):
        """Sends an event, using keyword arguments to create an Event

        >>> client.event(service='riemann-client', state='awesome')

        :param \*\*data: keyword arguments used for :py:func:`create_event`
        :returns: The response message from Riemann
        """
        return self.send_event(self.create_event(data))

    @staticmethod
    def create_dict(event):
        """Translates an Event object to a dictionary of event attributes

        All attributes are included, so ``create_dict(create_event(input))``
        may return more attributes than were present in the input.

        :param event: A protocol buffer ``Event`` object
        :returns: A dictionary of event attributes
        """

        data = dict()

        for descriptor, value in event.ListFields():
            if descriptor.name == 'tags':
                value = list(value)
            elif descriptor.name == 'attributes':
                value = dict(((a.key, a.value) for a in value))
            data[descriptor.name] = value

        return data

    def send_query(self, query):
        """Sends a query to the Riemann server

        :returns: The response message from Riemann
        """
        message = riemann_client.riemann_pb2.Msg()
        message.query.string = query
        return self.transport.send(message)

    def query(self, query):
        """Sends a query to the Riemann server

        >>> client.query('true')

        :returns: A list of event dictionaries taken from the response
        :raises Exception: if used with a :py:class:`.UDPTransport`
        """
        if isinstance(self.transport, riemann_client.transport.UDPTransport):
            raise Exception('Cannot query the Riemann server over UDP')
        response = self.send_query(query)
        return [self.create_dict(e) for e in response.events]


class QueuedClient(Client):
    """A Riemann client using a queue that can be used to batch send events.

    A message object is used as a queue, with the :py:meth:`.send_event` and
    :py:meth:`.send_events` methods adding new events to the message and the
    :py:meth:`.flush` sending the message.
    """

    def __init__(self, transport=None):
        super(QueuedClient, self).__init__(transport)
        self.clear_queue()

    def flush(self):
        """Sends the waiting message to Riemann

        :returns: The response message from Riemann
        """
        response = self.transport.send(self.queue)
        self.clear_queue()
        return response

    def send_event(self, event):
        """Adds a single event to the queued message

        :returns: None - nothing has been sent to the Riemann server yet
        """
        self.send_events((event,))
        return None

    def send_events(self, events):
        """Adds multiple events to the queued message

        :returns: None - nothing has been sent to the Riemann server yet
        """
        for event in events:
            self.queue.events.add().MergeFrom(event)
        return None

    def clear_queue(self):
        """Resets the message/queue to a blank :py:class:`.Msg` object"""
        self.queue = riemann_client.riemann_pb2.Msg()


if RLock and Timer:  # noqa
    class AutoFlushingQueuedClient(QueuedClient):
        """A Riemann client using a queue and a timer that will automatically
        flush its contents if either:
            - the queue size exceeds :param max_batch_size: or
            - more than :param max_delay: has elapsed since the last flush and
             the queue is non-empty.

        if :param stay_connected: is False, then the transport will be
        disconnected after each flush and reconnected at the beginning of
        the next flush.
        if :param clear_on_fail: is True, then the client will discard its
        buffer after the second retry in the event of a socket error.

        A message object is used as a queue, and the following methods are
        given:
            - :py:meth:`.send_event` - add a new event to the queue
            - :py:meth:`.send_events` add a tuple of new events to the queue
            - :py:meth:`.event` - add a new event to the queue from
               keyword arguments
            - :py:meth:`.events` - add new events to the queue from
               dictionaries
            - :py:meth:`.flush` - manually force flush the queue to the
               transport
        """

        def __init__(self, transport, max_delay=0.5, max_batch_size=100,
                     stay_connected=False, clear_on_fail=False):
            super(AutoFlushingQueuedClient, self).__init__(transport)
            self.stay_connected = stay_connected
            self.clear_on_fail = clear_on_fail
            self.max_delay = max_delay
            self.max_batch_size = max_batch_size
            self.lock = RLock()
            self.event_counter = 0
            self.last_flush = time.time()
            self.timer = None

            # start the timer
            self.start_timer()

        def connect(self):
            """Connect the transport if it is not already connected."""
            if not self.is_connected():
                self.transport.connect()

        def is_connected(self):
            """Check whether the transport is connected."""
            try:
                # this will throw an exception whenever socket isn't connected
                self.transport.socket.type
                return True
            except (AttributeError, RuntimeError, socket.error):
                return False

        def event(self, **data):
            """Enqueues an event, using keyword arguments to create an Event

            >>> client.event(service='riemann-client', state='awesome')

            :param \*\*data: keyword arguments used for :py:func:`create_event`
            """
            self.send_events((self.create_event(data),))

        def events(self, *events):
            """Enqueues multiple events in a single message

            >>> client.events({'service': 'riemann-client',
            >>>                'state': 'awesome'})

             :param \*events: event dictionaries for :py:func:`create_event`
             :returns: The response message from Riemann
            """
            self.send_events(self.create_event(evd) for evd in events)

        def send_events(self, events):
            """Enqueues multiple events

            :param events: A list or iterable of ``Event`` objects
            :returns: The response message from Riemann
            """
            with self.lock:
                for event in events:
                    self.queue.events.add().MergeFrom(event)
                    self.event_counter += 1
                    self.check_for_flush()

        def flush(self):
            """Sends the events in the queue to Riemann in a single protobuf
            message

            :returns: The response message from Riemann
            """
            response = None
            with self.lock:
                if not self.is_connected():
                    self.connect()
                try:
                    response = super(AutoFlushingQueuedClient, self).flush()
                except socket.error:
                    # log and retry
                    logger.warn("Socket error on flushing. "
                                "Attempting reconnect and retry...")
                    try:
                        self.transport.disconnect()
                        self.connect()
                        response = (
                            super(AutoFlushingQueuedClient, self).flush())
                    except:
                        logger.warn("Socket error on flushing "
                                    "second attempt. Batch discarded.")
                        self.transport.disconnect()
                        if self.clear_on_fail:
                            self.clear_queue()
                self.event_counter = 0
                if not self.stay_connected:
                    self.transport.disconnect()
                self.last_flush = time.time()
            self.start_timer()
            return response

        def check_for_flush(self):
            """Checks the conditions for flushing the queue"""
            if (self.event_counter >= self.max_batch_size or
                    (time.time() - self.last_flush) >= self.max_delay):
                self.flush()

        def start_timer(self):
            """Cycle the timer responsible for periodically flushing the queue
            """
            if self.timer:
                self.timer.cancel()
            self.timer = Timer(self.max_delay, self.check_for_flush)
            self.timer.daemon = True
            self.timer.start()

        def stop_timer(self):
            """Stops the current timer

            a :py:meth:`.flush` event will reactviate the timer
            """
            self.timer.cancel()
