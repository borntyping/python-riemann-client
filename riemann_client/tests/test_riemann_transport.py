from __future__ import absolute_import, unicode_literals

import py.test

import riemann_client.riemann_pb2
import riemann_client.transport


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
