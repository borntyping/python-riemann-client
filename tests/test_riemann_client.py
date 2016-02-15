from __future__ import absolute_import

import socket
import sys
import uuid

import py.test

import riemann_client.client
import riemann_client.riemann_pb2
import riemann_client.transport

if sys.version_info >= (3,):
    basestring = str


@py.test.fixture
def client(request, string_transport):
    client = riemann_client.client.Client(transport=string_transport)
    client.transport.connect()

    @request.addfinalizer
    def disconnect():
        client.transport.disconnect()

    return client


@py.test.fixture
def unique():
    return str(uuid.uuid4())


def test_default_transport():
    assert riemann_client.client.Client()


class TestClient(object):
    def test_service(self, client):
        client.event(service='test event')
        assert 'test event' in client.transport.string.getvalue()

    def test_default_hostname(self, client, event):
        event = client.event().events[0]
        assert socket.gethostname() == event.host
        assert socket.gethostname() in client.transport.string.getvalue()

    def test_custom_hostname(self, client):
        event = client.event(host="test.example.com").events[0]
        assert "test.example.com" == event.host
        assert "test.example.com" in client.transport.string.getvalue()

    def test_tags(self, client, unique):
        client.event(tags=[unique])
        assert unique in client.transport.string.getvalue()

    def test_attributes(self, client, unique):
        client.event(attributes={'key': unique})
        assert unique in client.transport.string.getvalue()

    def test_event_cls(self, event):
        assert isinstance(event, riemann_client.riemann_pb2.Event)

    def test_query(self, client):
        assert client.query('true') == []

    def test_udp_query(self):
        transport = riemann_client.transport.UDPTransport()
        client = riemann_client.client.Client(transport)

        with py.test.raises(Exception):
            client.query('true')

    def test_events(self, client):
        message = client.events({'service': 'one'}, {'service': 'two'})
        assert message.events[0].service == 'one'
        assert message.events[1].service == 'two'

    def test_events_len(self, client):
        message = client.events({'service': 'one'}, {'service': 'two'})
        assert len(message.events) == 2


@py.test.fixture
def event(unique):
    return riemann_client.client.Client.create_event({
        'host': 'test.example.com',
        'tags': [unique],
        'attributes': {
            unique: unique
        }
    })


class TestCreateEvent(object):
    def test_host(self, event):
        assert event.host == 'test.example.com'

    def test_tags(self, event, unique):
        assert unique in event.tags

    def test_attributes(self, event, unique):
        assert event.attributes[0].key == unique
        assert event.attributes[0].value == unique


@py.test.fixture
def event_as_dict(event):
    return riemann_client.client.Client.create_dict(event)


class TestCreateDict(object):
    def test_host(self, event, event_as_dict):
        assert event.host == event_as_dict['host']

    def test_host_type(self, event_as_dict):
        assert isinstance(event_as_dict['host'], basestring)

    def test_tags(self, event, event_as_dict):
        for tag in event.tags:
            assert tag in event_as_dict['tags']

    def test_tags_type(self, event_as_dict):
        assert isinstance(event_as_dict['tags'], list)

    def test_attibutes(self, event, event_as_dict):
        for attr in event.attributes:
            assert event_as_dict['attributes'][attr.key] == attr.value

    def test_attibutes_type(self, event_as_dict):
        assert isinstance(event_as_dict['attributes'], dict)
