"""Riemann protocol buffer client"""

from __future__ import absolute_import

import abc
import socket
import struct

import riemann.riemann_pb2


class RiemannError(Exception):
    """Error class for errors recived from the Riemann server"""
    pass


class Transport(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def disconnect(self):
        pass

    @abc.abstractmethod
    def write(self):
        pass

    @property
    def address(self):
        return self.host, self.port


class UDPTransport(Transport):
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def disconnect(self):
        self.socket.close()

    def write(self, message):
        self.socket.sendto(message.SerializeToString(), self.address)


class TCPTransport(Transport):
    def connect(self):
        self.socket = socket.create_connection(self.address)

    def disconnect(self):
        self.socket.close()

    def write(self, message):
        # Send the message to the server
        data = message.SerializeToString()
        self.socket.send(struct.pack('!I', len(data)) + data)

        # Return the server's response
        response_len = struct.unpack('!I', self.socket.recv(4))[0]
        response = riemann.riemann_pb2.Msg()
        response.ParseFromString(self.socket.recv(response_len))

        # Handle error messages
        if not response.ok:
            raise RiemannError(response.error)

        return response


class RetryingTCPTransport(TCPTransport):
    def write(self, message, tries=3):
        for i in xrange(reversed(tries)):
            try:
                response = super(RetryingTCPTransport, self).write(message)
            except (socket.error, struct.error, RiemannError) as error:
                if i <= 0:
                    raise error
            else:
                return response


class Client(object):
    """An abstract Riemann client"""

    def __init__(self, transport=None):
        self.transport = transport or UDPTransport

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
