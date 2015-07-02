from __future__ import absolute_import, unicode_literals

import sys

import py.test

import riemann_client.transport

if sys.version_info >= (3,):
    from io import StringIO as StringIO
else:
    from StringIO import StringIO


class StringTransport(riemann_client.transport.Transport):
    def connect(self):
        self.string = StringIO()
        self.counter = 0

    def send(self, message):
        self.string.write(str(message.SerializeToString()))
        self.counter += 1
        message.ok = True
        return message

    def disconnect(self):
        self.string.close()

    def __len__(self):
        return self.counter


@py.test.fixture
def string_transport():
    return StringTransport()