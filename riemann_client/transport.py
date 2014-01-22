"""Riemann TCP and UDP transports"""

from __future__ import absolute_import

import abc
import socket
import struct

import riemann_client.riemann_pb2


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

    @property
    def address(self):
        return self.host, self.port

    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def disconnect(self):
        pass

    @abc.abstractmethod
    def send(self):
        pass


class UDPTransport(Transport):
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def disconnect(self):
        self.socket.close()

    def send(self, message):
        self.socket.sendto(message.SerializeToString(), self.address)
        return NotImplemented


class TCPTransport(Transport):
    def connect(self):
        self.socket = socket.create_connection(self.address)
        self.socket.setblocking(True)

    def disconnect(self):
        self.socket.close()

    def send(self, message):
        message = message.SerializeToString()
        self.socket.sendall(struct.pack('!I', len(message)) + message)

        length = struct.unpack('!I', self.socket.recv(4))[0]
        response = riemann_client.riemann_pb2.Msg()
        response.ParseFromString(self.socket_recvall(socket, length))

        if not response.ok:
            raise RiemannError(response.error)

        return response

    @staticmethod
    def socket_recvall(socket, length, bufsize=4096):
        data = ""
        while len(data) < length:
            data += socket.recv(bufsize)
        return data
