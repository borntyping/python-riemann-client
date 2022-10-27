"""A Python Riemann client and command line tool"""

from .client import Client, QueuedClient
from .transport import (
    BlankTransport,
    RiemannError,
    SocketTransport,
    TCPTransport,
    TLSTransport,
    UDPTransport,
)

try:
    from .client import AutoFlushingQueuedClient
except ImportError:
    pass

__version__ = '6.4.0'
__author__ = 'Sam Clements <sam.clements@datasift.com>'

__all__ = (
    "AutoFlushingQueuedClient",
    "BlankTransport",
    "Client",
    "QueuedClient",
    "RiemannError",
    "SocketTransport",
    "TCPTransport",
    "TLSTransport",
    "UDPTransport",
)
