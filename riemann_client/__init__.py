"""A Python Riemann client and command line tool"""

from .client import (
    Client, QueuedClient  # noqa
)

from .transport import (
    RiemannError, SocketTransport, UDPTransport,  # noqa
    TCPTransport, TLSTransport, BlankTransport,   # noqa
)


try:
    from .client import AutoFlushingQueuedClient  # noqa
except ImportError:
    pass

__version__ = '6.4.0'
__author__ = 'Sam Clements <sam.clements@datasift.com>'
