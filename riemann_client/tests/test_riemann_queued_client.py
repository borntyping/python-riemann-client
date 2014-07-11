from __future__ import absolute_import, unicode_literals

import py.test
import uuid

import riemann_client.client
import riemann_client.riemann_pb2
import riemann_client.transport


@py.test.fixture
def queued_client(request, string_transport):
    """A Riemann client using the StringIO transport and QueuedClient"""
    client = riemann_client.client.QueuedClient(transport=string_transport)
    client.transport.connect()

    @request.addfinalizer
    def disconnect():
        client.transport.disconnect()

    return client


@py.test.fixture
def using_simple_queue(queued_client):
    """An event queue with a single event"""
    queued_client.event(service='test')


@py.test.fixture
def large_queue(queued_client):
    """An event queue with 100 events"""
    items = ['-->{0}<--'.format(i) for i in range(0, 1000)]
    for description in items:
        queued_client.event(service='queue', description=description)
    return items


@py.test.fixture
def unique():
    return str(uuid.uuid4())


@py.test.fixture
def event(unique):
    return riemann_client.client.Client.create_event({
        'host': 'test.example.com',
        'tags': [unique],
        'attributes': {
            unique: unique
        }
    })

def test_simple_queue_event(queued_client, using_simple_queue):
    assert queued_client.queue.events[0].service == 'test'


def test_simple_queue_length(queued_client, using_simple_queue):
    assert len(queued_client.queue.events) == 1


def test_simple_queue_event_not_sent(queued_client, using_simple_queue):
    assert "test" not in queued_client.transport.string.getvalue()


def test_simple_queue_event_sent(queued_client, using_simple_queue):
    queued_client.flush()
    assert "test" in queued_client.transport.string.getvalue()


def test_deciqueue_length(queued_client, large_queue):
    assert len(queued_client.queue.events) == len(large_queue)


def test_deciqueue_output(queued_client, large_queue):
    queued_client.flush()
    for description in large_queue:
        assert description in queued_client.transport.string.getvalue()


def test_deciqueue_flush(queued_client, large_queue):
    queued_client.flush()
    assert len(queued_client.queue.events) == 0


def test_send_many_events(queued_client, event):
    events = [event for i in range(0, 5)]
    queued_client.send_event(*events)
    assert len(queued_client.queue.events) == 5
