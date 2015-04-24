==============
riemann-client
==============

.. image:: http://img.shields.io/pypi/v/riemann-client.svg?style=flat-square
    :target: https://pypi.python.org/pypi/riemann-client

.. image:: http://img.shields.io/pypi/l/riemann-client.svg?style=flat-square
    :target: https://pypi.python.org/pypi/riemann-client

.. image:: http://img.shields.io/travis/borntyping/python-riemann-client/master.svg?style=flat-square
    :target: https://travis-ci.org/borntyping/python-riemann-client

|

A `Riemann <http://riemann.io/>`_ client library and command line tool for Python. It supports UDP and TCP transports, queries, and all metric types. The client library aims to provide a simple, minimal API does not require direct interaction with protocol buffers. There is also a queued client that can queue or batch events and then send them in a single message.

* `Source on GitHub <https://github.com/borntyping/python-riemann-client>`_
* `Documentation on Read the Docs <http://riemann-client.readthedocs.org/en/latest/>`_
* `Packages on PyPI <https://pypi.python.org/pypi/riemann-client>`_

Usage
-----

As a command line tool::

	riemann-client [--host HOST] [--port PORT] send [-s SERVICE] [-S STATE] [-m METRIC] [...]
	riemann-client [--host HOST] [--port PORT] query QUERY

The host and port used by the command line tool can also be set with the ``RIEMANN_HOST`` and ``RIEMANN_PORT`` environment variables. By default, ``localhost:5555`` will be used.

As a library::

	import riemann_client.client

	with riemann_client.client.Client() as client:
		client.event(service="riemann-client", state="awesome")
		client.query("service = 'riemann-client'")

A more detailed example, using both a non-default transport and a queued client::

	from riemann_client.transport import TCPTransport
	from riemann_client.client import QueuedClient

	with QueuedClient(TCPTransport("localhost", 5555)) as client:
		client.event(service="one", metric_f=0.1)
		client.event(service="two", metric_f=0.2)
		client.flush()

The ``QueuedClient`` class modifies the ``event()`` method to add events to a queue instead of immediately sending them, and adds the ``flush()`` method to send the current event queue as a single message.

.. toctree::
   :hidden:

   riemann-client client API <riemann_client.client>
   riemann-client transport API <riemann_client.transport>

Installation
------------

``riemann-client`` requires Python 2.6 or above, and can be installed with ``pip install riemann-client``. It will use Google's `protobuf <https://pypi.python.org/pypi/protobuf>`_ library when running under Python 2, and `GreatFruitOmsk <https://github.com/GreatFruitOmsk>`_'s `protobuf-py3 <https://pypi.python.org/pypi/protobuf-py3>`_ when running under Python 3. Python 3 support is experimental and is likley to use Google's `protobuf` once it supports Python 3 fully.

Requirements
^^^^^^^^^^^^

* `click <http://click.pocoo.org/>`_
* `protobuf <https://pypi.python.org/pypi/protobuf>`_ (when using Python 2)
* `protobuf <https://pypi.python.org/pypi/protobuf-py3>`_ (when using Python 3)

Changelog
---------

Version 6.0.0
^^^^^^^^^^^^^

* ``riemann_client.client.Client.create_dict`` only returns event fields that are set on the Protocol Buffers ``Event`` object
* ``riemann-client send ...``` only outputs fields that were set on the sent message

Version 5.1.0
^^^^^^^^^^^^^

* Added Python 3 support
* Changed ``riemann_client.riemann_pb2`` to wrap ``_py2`` and ``_py3`` modules
* Changed ``setup.py`` to dynamically select a ``protobuf`` dependency

Version 5.0.x
^^^^^^^^^^^^^

* Added API documentation (`riemann-client.readthedocs.org <http://riemann-client.readthedocs.org/en/latest/>`_)
* Replaced ``argparse`` with ``click`` for an improved CLI
* Various command line parameters changed
* ``--event-host`` became ``--host``
* ``--print`` was removed, ``send`` always prints the sent event
* Minor fixes to ``QueuedClient`` API
* ``UDPTransport.send`` returns ``None`` instead of ``NotImplemented``

Version 4.2.x
^^^^^^^^^^^^^

* Added ``events()`` and ``send_events()`` methods to the client
* Added ``clear_queue()`` method to the queued client
* Add ``--timeout`` option for TCP based transports

Version 4.1.x
^^^^^^^^^^^^^

* Full Riemann protocol support (TLS transport, event attributes)
* Fixes for multiple broken features (``--tags``, ``--print``)
* Raise errors when clients are used incorrectly
* Client displays errors from Riemann nicely
* Relaxed version requirements to fit CentOS 6 packages

Version 3.0.x
^^^^^^^^^^^^^

* Renamed module from ``riemann`` to ``riemann_client``
* Command line interface was rewritten, and is now the only part of the library that respects the ``RIEMANN_HOST`` and ``RIEMANN_PORT`` environment variables
* Support for querying the Riemann index was added
* Internally, transports now define ``send`` instead of ``write``, and ``TCPTransport.send`` returns Riemann's response message

Licence
-------

``riemann-client`` is licensed under the `MIT Licence <http://opensource.org/licenses/MIT>`_. The protocol buffer definition is sourced from the `Riemann Java client <https://github.com/aphyr/riemann-java-client/blob/0c4a1a255be6f33069d7bb24d0cc7efb71bf4bc8/src/main/proto/riemann/proto.proto>`_, which is licensed under the `Apache Licence <http://www.apache.org/licenses/LICENSE-2.0>`_.

Authors
-------

``riemann-client`` was written by `Sam Clements <https://github.com/borntyping>`_, while working at `DataSift <https://github.com/datasift>`_.

.. image:: https://0.gravatar.com/avatar/8dd5661684a7385fe723b7e7588e91ee?d=https%3A%2F%2Fidenticons.github.com%2Fe83ef7586374403a328e175927b98cac.png&r=x&s=40
.. image:: https://1.gravatar.com/avatar/a3a6d949b43b6b880ffb3e277a65f49d?d=https%3A%2F%2Fidenticons.github.com%2F065affbc170e2511eeacb3bd0e975ec1.png&r=x&s=40
