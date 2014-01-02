"""Riemann protocol buffer client"""

from __future__ import absolute_import

import socket

import riemann.riemann_pb2
import riemann.transport


class Client(object):
    """An abstract Riemann client"""

    def __init__(self, transport=None):
        if transport is None:
            transport = riemann.transport.TCPTransport()
        self.transport = transport

    def __enter__(self):
        self.transport.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.transport.disconnect()

    @staticmethod
    def create_event(data):
        """Creates an Event from a dictionary"""
        data.setdefault('host', socket.gethostname())
        data.setdefault('tags', list())
        event = riemann.riemann_pb2.Event()
        event.tags.extend(data.pop('tags'))
        for name, value in data.items():
            setattr(event, name, value)
        return event

    def send_event(self, event):
        """Wraps an event in a message and sends it to Riemann"""
        message = riemann.riemann_pb2.Msg()
        message.events.extend([event])
        self.transport.write(message)
        return event

    def event(self, **data):
        """Sends an event"""
        return self.send_event(self.create_event(data))

    def query(self, *args, **kwargs):
        raise NotImplemented("Querying is not yet supported")


class QueuedClient(Client):
    """A queued Riemann client"""

    def __init__(self, *args, **kwargs):
        super(QueuedClient, self).__init__(*args, **kwargs)
        self.queue = riemann.riemann_pb2.Msg()

    def flush(self):
        """Sends the waiting message to Riemann"""
        self.transport.write(self.queue)
        self.queue = riemann.riemann_pb2.Msg()

    def send_event(self, event):
        self.queue.events.extend([event])
        return event
