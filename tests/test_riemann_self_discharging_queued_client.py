from __future__ import absolute_import, unicode_literals

import py.test
import time

import riemann_client.client
import riemann_client.riemann_pb2
import riemann_client.transport


@py.test.fixture
def blank_transport():
    return riemann_client.transport.BlankTransport()


@py.test.fixture
def self_discharging_queued_client(request, blank_transport):
    """A Riemann client using the StringIO transport and 
    SelfDischargingQueuedClient with max_delay=300 and 
    max_batch_size=5000"""
    client = riemann_client.client.SelfDischargingQueuedClient(
        transport=blank_transport,
        max_delay=300,
        max_batch_size=5000,
        stay_connected=True)
    client.transport.connect()

    @request.addfinalizer
    def disconnect():
        client.transport.disconnect()

    return client


@py.test.fixture
def self_discharging_queued_client_delay1(request, blank_transport):
    """A Riemann client using the StringIO transport and 
    SelfDischargingQueuedClient with max_delay=1 and
    max_batch_size=5000"""
    client = riemann_client.client.SelfDischargingQueuedClient(
        transport=blank_transport,
        max_delay=1,
        max_batch_size=5000,
        stay_connected=True)
    client.transport.connect()

    @request.addfinalizer
    def disconnect():
        client.transport.disconnect()

    return client


@py.test.fixture
def self_discharging_queued_client_batch5(request, blank_transport):
    """A Riemann client using the StringIO transport and 
    SelfDischargingQueuedClient with max_delay=300 and
    max_batch_size=5"""
    client = riemann_client.client.SelfDischargingQueuedClient(
        transport=blank_transport,
        max_delay=300,
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
    assert self_discharging_queued_client.queue.events[0].service == 'test'


def test_simple_queue_length(self_discharging_queued_client, using_simple_queue):
    assert len(self_discharging_queued_client.queue.events) == 1


def test_simple_queue_event_not_sent(self_discharging_queued_client, using_simple_queue):
    assert len(self_discharging_queued_client.transport.messages) == 0


def test_simple_queue_event_sent(self_discharging_queued_client, using_simple_queue):
    self_discharging_queued_client.flush()
    assert len(self_discharging_queued_client.transport.messages) == 1


def test_deciqueue_length(self_discharging_queued_client, large_queue):
    assert len(self_discharging_queued_client.queue.events) == len(large_queue)


def test_deciqueue_output(self_discharging_queued_client, large_queue):
    self_discharging_queued_client.flush()
    # note that these will be ordered, and all events will be in a single 
    # protobuf flush, so we can find them in messages[0] 
    for idx, description in enumerate(large_queue):
        assert (description == self_discharging_queued_client.
                               transport.messages[idx].description)


def test_deciqueue_flush(self_discharging_queued_client, large_queue):
    self_discharging_queued_client.flush()
    assert len(self_discharging_queued_client.queue.events) == 0


def test_clear_queue(self_discharging_queued_client, using_simple_queue):
    self_discharging_queued_client.clear_queue()
    assert len(self_discharging_queued_client.queue.events) == 0


def test_batchsize_autoflush(self_discharging_queued_client_batch5):
    self_discharging_queued_client_batch5.clear_queue()
    sent = 0
    to_send = 100
    for i in range(to_send):
        self_discharging_queued_client_batch5.event(service='test', description='{:03d}'.format(i))
        sent += 1
    assert len(self_discharging_queued_client_batch5.queue.events) == 0
    assert len(self_discharging_queued_client_batch5.transport) == sent
    assert ('000' == self_discharging_queued_client_batch5.
                     transport.messages[0].description)
    assert ('{:03d}'.format(to_send - 1) == 
            self_discharging_queued_client_batch5.transport.
            messages[-1].description)


# def test_timer_autoflush(self_discharging_queued_client):
#     self_discharging_queued_client.clear_queue()
#     time_0 = time.time()
#     self_discharging_queued_client.event(service='test')
#     assert len(self_discharging_queued_client.transport) == 0
#     assert len(self_discharging_queued_client.queue) == 1
#     time.sleep(1.05)
#     assert len(self_discharging_queued_client.transport) == 1
#     assert len(self_discharging_queued_client.queue) == 0
