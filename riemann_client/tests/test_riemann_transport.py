from __future__ import absolute_import, unicode_literals

import py.test

import riemann_client.riemann_pb2
import riemann_client.transport

from riemann_client.transport import socket_recvall


class FakeSocket(object):
        def __init__(self):
            self.data = [b'hello', b'world', b'']

        def recv(self, bufsize):
            return self.data.pop(0)


def test_socket_recvall():
    assert socket_recvall(FakeSocket(), 10) == b'helloworld'


def test_socket_recvall_short():
    assert socket_recvall(FakeSocket(), 5) == b'hello'


@py.test.fixture
def tcp_transport():
    return riemann_client.transport.TCPTransport()


def test_not_yet_connected(tcp_transport):
    with py.test.raises(RuntimeError):
        tcp_transport.send(riemann_client.riemann_pb2.Msg())


def test_address_property(tcp_transport):
    assert tcp_transport.address == (tcp_transport.host, tcp_transport.port)


def test_transport_enter(string_transport):
    assert not hasattr(string_transport, 'string')
    with string_transport:
        assert hasattr(string_transport, 'string')
