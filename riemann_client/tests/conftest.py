from __future__ import absolute_import, unicode_literals

import StringIO

import py.test

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
def string_transport():
    return StringTransport()
