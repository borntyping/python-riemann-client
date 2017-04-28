"""Wraps the riemann_pb2_py2 and riemann_pb2_py3 modules"""

import sys

__all__ = ['Event', 'Msg', 'Query', 'Attribute']

if sys.version_info >= (3,):
    from riemann_client.riemann_py3_pb2 import (Event, Msg, Query, Attribute)
else:
    from riemann_client.riemann_py2_pb2 import (Event, Msg, Query, Attribute)
