=====================
python-riemann-client
=====================

.. image:: https://pypip.in/v/riemann-client/badge.png
    :target: https://pypi.python.org/pypi/riemann-client

.. image:: https://travis-ci.org/borntyping/python-riemann-client.png?branch=master
    :target: https://travis-ci.org/borntyping/python-riemann-client

A `Riemann <http://riemann.io/>`_ client and command line tool.

Installation
------------

::

	pip install riemann-client


Usage
-----

::

	riemann-client [host] [port] [-t {tcp,udp}] send [-s SERVICE] [-S STATE] [-m METRIC] [...]

See `riemann-client --help` for more options.

Requirements
------------

* `argparse <https://pypi.python.org/pypi/argparse>`_
* `protobuf <https://pypi.python.org/pypi/protobuf>`_

Licence
-------

python-riemann-client is licensed under the `MIT Licence <http://opensource.org/licenses/MIT>`_. The protocol buffer definition is sourced from the `Riemann Java client <https://github.com/aphyr/riemann-java-client/blob/0c4a1a255be6f33069d7bb24d0cc7efb71bf4bc8/src/main/proto/riemann/proto.proto>`_, which is licensed under the `Apache Licence <http://www.apache.org/licenses/LICENSE-2.0>`_.

Authors
-------

Supermann was written by `Sam Clements <https://github.com/borntyping>`_, while working at `DataSift <https://github.com/datasift>`_.

.. image:: https://0.gravatar.com/avatar/8dd5661684a7385fe723b7e7588e91ee?d=https%3A%2F%2Fidenticons.github.com%2Fe83ef7586374403a328e175927b98cac.png&r=x&s=40
.. image:: https://1.gravatar.com/avatar/a3a6d949b43b6b880ffb3e277a65f49d?d=https%3A%2F%2Fidenticons.github.com%2F065affbc170e2511eeacb3bd0e975ec1.png&r=x&s=40
