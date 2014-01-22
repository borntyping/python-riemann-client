from __future__ import absolute_import, unicode_literals

import socket
import StringIO

import py.test

import riemann_client.client
import riemann_client.riemann_pb2
import riemann_client.transport


class StringTransport(riemann_client.transport.Transport):
    def connect(self):
        self.string = StringIO.StringIO()

    def send(self, message):
        self.string.write(message.SerializeToString())
        message.ok = True
        return message

    def disconnect(self):
        self.string.close()


@py.test.fixture
def client(request):
    client = riemann_client.client.Client(transport=StringTransport())
    client.transport.connect()

    @request.addfinalizer
    def disconnect():
        client.transport.disconnect()

    return client


@py.test.fixture
def event(client):
    """Send and return a blank event"""
    message = client.event()
    return message.events[0]


class TestClient(object):
    def test_service(self, client):
        client.event(service='test event')
        assert 'test event' in client.transport.string.getvalue()

    def test_default_hostname(self, client, event):
        assert socket.gethostname() == event.host
        assert socket.gethostname() in client.transport.string.getvalue()

    def test_custom_hostname(self, client):
        event = client.event(host="test.example.com").events[0]
        assert "test.example.com" == event.host
        assert "test.example.com" in client.transport.string.getvalue()

    def test_tags(self, client):
        client.event(tags=['tag-1', 'tag-2'])
        assert "tag-1" in client.transport.string.getvalue()

    def test_event_cls(self, event):
        assert isinstance(event, riemann_client.riemann_pb2.Event)

    def test_query(self, client):
        assert client.query("true") == []


@py.test.fixture
def queued_client(request):
    client = riemann_client.client.QueuedClient(transport=StringTransport())
    client.transport.connect()

    @request.addfinalizer
    def disconnect():
        client.transport.disconnect()

    return client


class TestQueuedClient(object):
    def test_queue(self, queued_client):
        event = queued_client.event(service="test")
        assert event in queued_client.queue.events
        assert len(queued_client.queue.events) == 1
        assert "test" not in queued_client.transport.string.getvalue()

        queued_client.flush()
        assert "test" in queued_client.transport.string.getvalue()
        assert len(queued_client.queue.events) == 0
