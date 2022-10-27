"""Wraps the riemann_py2_pb2 and riemann_py3_pb2 modules"""

import sys

__all__ = ['Event', 'Msg', 'Query', 'Attribute']

if sys.version_info >= (3,):
    from .riemann_py3_pb2 import (Event, Msg, Query, Attribute)
else:
    from .riemann_py2_pb2 import (Event, Msg, Query, Attribute)
