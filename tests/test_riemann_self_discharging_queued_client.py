from __future__ import absolute_import, unicode_literals

import py.test
import time

import riemann_client.client
import riemann_client.riemann_pb2
import riemann_client.transport

@py.test.fixture
def self_discharging_queued_client(request, string_transport):
    """A Riemann client using the StringIO transport and QueuedClient"""
    print dir(riemann_client.client)
    print riemann_client.client.__file__
    client = riemann_client.client.SelfDischargingQueuedClient(
        transport=string_transport,
        max_delay=30,
        max_batch_size=500,
        stay_connected=True)
    client.transport.connect()

    @request.addfinalizer
    def disconnect():
        client.transport.disconnect()

    return client


@py.test.fixture
def self_discharging_queued_client_delay1(request, string_transport):
    """A Riemann client using the StringIO transport and QueuedClient"""
    client = riemann_client.client.SelfDischargingQueuedClient(
        transport=string_transport,
        max_delay=1,
        max_batch_size=500,
        stay_connected=True)
    client.transport.connect()

    @request.addfinalizer
    def disconnect():
        client.transport.disconnect()

    return client


@py.test.fixture
def self_discharging_queued_client_batch5(request, string_transport):
    """A Riemann client using the StringIO transport and QueuedClient"""
    client = riemann_client.client.SelfDischargingQueuedClient(
        transport=string_transport,
        max_delay=30,
        max_batch_size=5,
        stay_connected=True)
    client.transport.connect()

    @request.addfinalizer
    def disconnect():
        client.transport.disconnect()

    return client


@py.test.fixture
def using_simple_queue(self_discharging_queued_client):
    """An event queue with a single event"""
    self_discharging_queued_client.event(service='test')


@py.test.fixture
def large_queue(self_discharging_queued_client):
    """An event queue with 100 events"""
    items = ['-->{0}<--'.format(i) for i in range(0, 1000)]
    for description in items:
        self_discharging_queued_client.event(service='queue', description=description)
    return items


def test_simple_queue_event(self_discharging_queued_client, using_simple_queue):
    assert 1 == 0
    assert self_discharging_queued_client.queue.events[0].service == 'test'


# def test_simple_queue_length(self_discharging_queued_client, using_simple_queue):
#     assert len(self_discharging_queued_client.queue.events) == 1
#
#
# def test_simple_queue_event_not_sent(self_discharging_queued_client, using_simple_queue):
#     assert "test" not in self_discharging_queued_client.transport.string.getvalue()
#
#
# def test_simple_queue_event_sent(self_discharging_queued_client, using_simple_queue):
#     self_discharging_queued_client.flush()
#     assert "test" in self_discharging_queued_client.transport.string.getvalue()
#
#
# def test_deciqueue_length(self_discharging_queued_client, large_queue):
#     assert len(self_discharging_queued_client.queue.events) == len(large_queue)
#
#
# def test_deciqueue_output(self_discharging_queued_client, large_queue):
#     self_discharging_queued_client.flush()
#     for description in large_queue:
#         assert description in self_discharging_queued_client.transport.string.getvalue()
#
#
# def test_deciqueue_flush(self_discharging_queued_client, large_queue):
#     self_discharging_queued_client.flush()
#     assert len(self_discharging_queued_client.queue.events) == 0
#
#
# def test_clear_queue(self_discharging_queued_client, using_simple_queue):
#     self_discharging_queued_client.clear_queue()
#     assert len(self_discharging_queued_client.queue.events) == 0
#
#
# def test_batchsize_flush(self_discharging_queued_client_batch5):
#     self_discharging_queued_client.clear_queue()
#     sent = 0
#     for i in range(self_discharging_queued_client.max_batch_size):
#         self_discharging_queued_client.event(service='test')
#         sent += 1
#     assert len(self_discharging_queued_client.queue.events) == 0
#     assert len(self_discharging_queued_client.transport) == sent
#
#
# def test_auto_discharge(self_discharging_queued_client):
#     self_discharging_queued_client.clear_queue()
#     time_0 = time.time()
#     self_discharging_queued_client.event(service='test')
#     assert len(self_discharging_queued_client.transport) == 0
#     assert len(self_discharging_queued_client.queue) == 1
#     time.sleep(1.05)
#     assert len(self_discharging_queued_client.transport) == 1
#     assert len(self_discharging_queued_client.queue) == 0
