"""Riemann TCP and UDP transports"""

from __future__ import absolute_import

import abc
import socket
import ssl
import struct

import riemann_client.riemann_pb2


# Default arguments
HOST = 'localhost'
PORT = 5555
TIMEOUT = None


def socket_recvall(socket, length, bufsize=4096):
    """Recives bytes from a socket until the buffer is the requested length"""
    data = ""
    while len(data) < length:
        data += socket.recv(bufsize)
    return data


class RiemannError(Exception):
    """Error class for errors recived from the Riemann server"""
    pass


class Transport(object):
    """Abstract Transport definition"""

    __metaclass__ = abc.ABCMeta

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
    def send(self):
        pass


class SocketTransport(Transport):
    """Provides common functionality for Transports using sockets"""

    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port

    @property
    def address(self):
        return self.host, self.port

    @property
    def socket(self):
        """Checks that the socket attribute has been created before use"""
        if not hasattr(self, '_socket'):
            raise RuntimeError("Transport has not been connected!")
        return self._socket

    @socket.setter
    def socket(self, value):
        self._socket = value


class UDPTransport(SocketTransport):
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.timeout)

    def disconnect(self):
        self.socket.close()

    def send(self, message):
        self.socket.sendto(message.SerializeToString(), self.address)
        return NotImplemented


class TCPTransport(SocketTransport):
    def __init__(self, host=HOST, port=PORT, timeout=TIMEOUT):
        super(TCPTransport, self).__init__(host, port)
        self.timeout = timeout

    def connect(self):
        self.socket = socket.create_connection(self.address, self.timeout)

    def disconnect(self):
        self.socket.close()

    def send(self, message):
        message = message.SerializeToString()
        self.socket.sendall(struct.pack('!I', len(message)) + message)

        length = struct.unpack('!I', self.socket.recv(4))[0]
        response = riemann_client.riemann_pb2.Msg()
        response.ParseFromString(socket_recvall(self.socket, length))

        if not response.ok:
            raise RiemannError(response.error)

        return response


class TLSTransport(TCPTransport):
    def __init__(self, host=HOST, port=PORT, timeout=TIMEOUT, ca_certs=None):
        super(TLSTransport, self).__init__(host, port, timeout)
        self.ca_certs = ca_certs

    def connect(self):
        super(TLSTransport, self).connect()
        self.socket = ssl.wrap_socket(
            self.socket,
            ssl_version=ssl.PROTOCOL_TLSv1,
            cert_reqs=ssl.CERT_REQUIRED,
            ca_certs=self.ca_certs)
