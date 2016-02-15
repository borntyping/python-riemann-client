from __future__ import absolute_import

import py.test
import socket
import time

import riemann_client.client
import riemann_client.riemann_pb2
import riemann_client.transport


@py.test.fixture
def blank_transport():
    return riemann_client.transport.BlankTransport()


class BrokenTransport(riemann_client.transport.Transport):
    def connect(self):
        pass

    def disconnect(self):
        pass

    def send(self, *args, **kwargs):
        raise socket.error(32, '[Errno 32] Broken pipe')


@py.test.fixture
def broken_transport():
    return BrokenTransport()


@py.test.fixture
def auto_flushing_queued_client(request, blank_transport):
    """A Riemann client using the StringIO transport and
    AutoFlushingQueuedClient with max_delay=300 and
    max_batch_size=5000"""
    client = riemann_client.client.AutoFlushingQueuedClient(
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
def auto_flushing_queued_client_delay(request, blank_transport):
    """A Riemann client using the StringIO transport and
    AutoFlushingQueuedClient with max_delay=1 and
    max_batch_size=5000"""
    client = riemann_client.client.AutoFlushingQueuedClient(
        transport=blank_transport,
        max_delay=0.05,
        max_batch_size=5000,
        stay_connected=True)
    client.transport.connect()

    @request.addfinalizer
    def disconnect():
        client.transport.disconnect()

    return client


@py.test.fixture
def auto_flushing_queued_client_batch5(request, blank_transport):
    """A Riemann client using the StringIO transport and
    AutoFlushingQueuedClient with max_delay=300 and
    max_batch_size=5"""
    client = riemann_client.client.AutoFlushingQueuedClient(
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
def auto_flushing_queued_client_batch5_broken_f(request, broken_transport):
    """A Riemann client using the StringIO transport and
    AutoFlushingQueuedClient with max_delay=300 and
    max_batch_size=5"""
    client = riemann_client.client.AutoFlushingQueuedClient(
        transport=broken_transport,
        max_delay=300,
        max_batch_size=5,
        stay_connected=True,
        clear_on_fail=False)
    client.transport.connect()

    @request.addfinalizer
    def disconnect():
        client.transport.disconnect()

    return client


@py.test.fixture
def auto_flushing_queued_client_batch5_broken_t(request, broken_transport):
    """A Riemann client using the StringIO transport and
    AutoFlushingQueuedClient with max_delay=300 and
    max_batch_size=5"""
    client = riemann_client.client.AutoFlushingQueuedClient(
        transport=broken_transport,
        max_delay=300,
        max_batch_size=5,
        stay_connected=True,
        clear_on_fail=True)
    client.transport.connect()

    @request.addfinalizer
    def disconnect():
        client.transport.disconnect()

    return client


@py.test.fixture
def using_simple_queue(auto_flushing_queued_client):
    """An event queue with a single event"""
    auto_flushing_queued_client.event(service='test')


@py.test.fixture
def large_queue(auto_flushing_queued_client):
    """An event queue with 100 events"""
    items = ['-->{0}<--'.format(i) for i in range(0, 1000)]
    for description in items:
        auto_flushing_queued_client.event(service='queue',
                                          description=description)
    return items


def test_simple_queue_event(auto_flushing_queued_client, using_simple_queue):
    assert auto_flushing_queued_client.queue.events[0].service == 'test'


def test_simple_queue_length(auto_flushing_queued_client, using_simple_queue):
    assert len(auto_flushing_queued_client.queue.events) == 1


def test_simple_queue_event_not_sent(auto_flushing_queued_client,
                                     using_simple_queue):
    assert len(auto_flushing_queued_client.transport.events) == 0


def test_simple_queue_event_sent(auto_flushing_queued_client,
                                 using_simple_queue):
    auto_flushing_queued_client.flush()
    assert len(auto_flushing_queued_client.transport.events) == 1


def test_deciqueue_length(auto_flushing_queued_client, large_queue):
    assert len(auto_flushing_queued_client.queue.events) == len(large_queue)


def test_deciqueue_output(auto_flushing_queued_client, large_queue):
    auto_flushing_queued_client.flush()
    # note that these will be ordered, and all events will be in a single
    # protobuf flush, so we can find them in messages[0]
    for idx, description in enumerate(large_queue):
        assert (description == auto_flushing_queued_client.
                transport.events[idx].description)


def test_deciqueue_flush(auto_flushing_queued_client, large_queue):
    auto_flushing_queued_client.flush()
    assert len(auto_flushing_queued_client.queue.events) == 0


def test_clear_queue(auto_flushing_queued_client, using_simple_queue):
    auto_flushing_queued_client.clear_queue()
    assert len(auto_flushing_queued_client.queue.events) == 0


def test_batchsize_autoflush(auto_flushing_queued_client_batch5):
    auto_flushing_queued_client_batch5.clear_queue()
    sent = 0
    to_send = 100
    for i in range(to_send):
        auto_flushing_queued_client_batch5.event(
            service='test', description='{0:03d}'.format(i))
        sent += 1
    assert len(auto_flushing_queued_client_batch5.queue.events) == 0
    assert len(auto_flushing_queued_client_batch5.transport) == sent
    assert ('000' == auto_flushing_queued_client_batch5.
            transport.events[0].description)
    assert ('{0:03d}'.format(to_send - 1) ==
            auto_flushing_queued_client_batch5.transport.
            events[-1].description)


def test_timer_autoflush(auto_flushing_queued_client_delay):
    auto_flushing_queued_client_delay.clear_queue()
    auto_flushing_queued_client_delay.event(service='test',
                                            description='timer_test')
    assert len(auto_flushing_queued_client_delay.transport) == 0
    assert len(auto_flushing_queued_client_delay.queue.events) == 1
    time.sleep(0.1)
    assert len(auto_flushing_queued_client_delay.transport) == 1
    assert len(auto_flushing_queued_client_delay.queue.events) == 0
    assert ('timer_test' == auto_flushing_queued_client_delay.
            transport.events[0].description)


def test_clear_on_fail_false(auto_flushing_queued_client_batch5_broken_f):
    auto_flushing_queued_client_batch5_broken_f.clear_queue()
    sent = 0
    to_send = 10
    for i in range(to_send):
        auto_flushing_queued_client_batch5_broken_f.event(
            service='test', description='{0:03d}'.format(i))
        sent += 1
    assert (len(auto_flushing_queued_client_batch5_broken_f.queue.events) ==
            sent)


def test_clear_on_fail_true(auto_flushing_queued_client_batch5_broken_t):
    auto_flushing_queued_client_batch5_broken_t.clear_queue()
    sent = 0
    to_send = 10
    for i in range(to_send):
        auto_flushing_queued_client_batch5_broken_t.event(
            service='test', description='{0:03d}'.format(i))
        sent += 1
    assert (len(auto_flushing_queued_client_batch5_broken_t.queue.events) ==
            0)
