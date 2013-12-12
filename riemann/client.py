"""Riemann protocol buffer client"""

from __future__ import absolute_import, unicode_literals

import abc
import socket

import riemann.riemann_pb2


class Client(object):
    """An abstract Riemann client"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, host, port=5555):
        self.host = host
        self.port = port
        self.create_next_message()

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

    def create_next_message(self):
        """Creates a Msg object to act as a queue"""
        self.next = riemann.riemann_pb2.Msg()

    def queue_events(self, *events):
        """Adds events to the next message"""
        self.next.events.extend(events)

    def send_next_message(self):
        """Sends the waiting message to Riemann"""
        self.write(self.next)
        self.create_next_message()

    def event(self, service, **data):
        """Creates an event and adds it to the next message"""
        event = riemann.riemann_pb2.Event()
        event.service = service
        event.tags.append('supermann')
        event.tags.extend(data.pop('tags', list()))
        data.setdefault('host', socket.gethostname())
        for name, value in data.items():
            setattr(event, name, value)
        self.queue_events(event)


class UDPClient(Client):
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def disconnect(self):
        self.socket.close()

    def write(self, message):
        self.socket.sendto(message.SerializeToString(), (self.host, self.port))
        return message
