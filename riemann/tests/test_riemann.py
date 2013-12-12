from __future__ import absolute_import, unicode_literals

import StringIO

import py.test

import riemann.client


def test_abstract_client():
    with py.test.raises(TypeError):
        riemann.client.Client()


class Client(riemann.client.Client):
    def connect(self):
        self.string = StringIO.StringIO()

    def write(self, message):
        self.string.write(message.SerializeToString())

    def disconnect(self):
        self.string.close()


class TestClient(object):
    def test_queue(self):
        with Client(None, None) as client:
            client.event('test event', description="This is a test event")
            client.send_next_message()
            assert 'test event' in client.string.getvalue()
