==============
riemann-client
==============

.. image:: https://pypip.in/v/riemann-client/badge.png
    :target: https://pypi.python.org/pypi/riemann-client

.. image:: https://travis-ci.org/borntyping/python-riemann-client.png?branch=master
    :target: https://travis-ci.org/borntyping/python-riemann-client

A `Riemann <http://riemann.io/>`_ client library and command line tool for Python. It supports UDP and TCP transports, queries, and all metric types. However, it does not currently support event attributes or a SSL TCP transport.

The client library aims to provide a simple, minimal API does not require direct interaction with protocol buffers (though it does allow using the protobuf API directly, allowing you to use unsupported features such as event attributes). There is also a queued client that can queue events and then send in a single message.

Usage
-----

As a command line tool::

	riemann-client [--host HOST] [--port PORT] send [-s SERVICE] [-S STATE] [-m METRIC] [...]
	riemann-client [--host HOST] [--port PORT] query '<query>'

The host and port used by the command line tool can also be set with the ``RIEMANN_HOST`` and ``RIEMANN_PORT`` environment variables. By default, ``localhost:5555`` will be used.

As a library::

	import riemann_client.client

	with riemann_client.client.Client() as client:
		client.event(service='riemann-client', state='awesome')
		client.query("service = 'riemann-client'")

A more detailed example, using both a non-default transport and a queued client::

	from riemann_client.transport import TCPTransport
	from riemann_client.client import QueuedClient

	with QueuedClient(TCPTransport('localhost', 5555)) as client:
		client.event(service='one', metric_f=1)
		client.event(service='two', metric_f=2)
		client.flush()

The ``QueuedClient`` class modifies the ``event()`` method to add events to a queue instead of immediately sending them, and adds the ``flush()`` method to send the current event queue as a single message.

Installation
------------

``riemann-client`` requires Python 2.6 or 2.7, and can be installed with ``pip install riemann-client``. Python 3 is not supported due to the dependency on the Google `protobuf <https://pypi.python.org/pypi/protobuf>`_ package. You can also use the provided makefile to build and distribute an RPM using [fpm](https://github.com/jordansissel/fpm).

Requirements
^^^^^^^^^^^^

* `argparse <https://pypi.python.org/pypi/argparse>`_
* `protobuf <https://pypi.python.org/pypi/protobuf>`_

Changelog
---------

Version numbers use the `semver <http://semver.org/>`_ specification. A new major version indicates breaking changes.

Version 3.1.x
^^^^^^^^^^^^^

* Relaxed version requirements to fit CentOS 6 packages
* ~~Added Makefile and specfile for building RPMs with rpmbuild~~
* Added Makefile to build RPMs with `fpm <https://github.com/jordansissel/fpm>`_

Version 3.0.0
^^^^^^^^^^^^^

* Renamed module from ``riemann`` to ``riemann_client``
* Command line interface was rewritten, and is now the only part of the library that respects the RIEMANN_HOST and RIEMANN_PORT environment variables
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
