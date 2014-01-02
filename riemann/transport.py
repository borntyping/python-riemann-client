"""Riemann TCP and UDP transports"""

from __future__ import absolute_import

import abc
import os
import socket
import struct

import riemann.riemann_pb2


class RiemannError(Exception):
    """Error class for errors recived from the Riemann server"""
    pass


class Transport(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, host=None, port=None):
        self.host = host or os.environ.get('RIEMANN_HOST', 'localhost')
        self.port = port or os.environ.get('RIEMANN_PORT', 5555)

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
