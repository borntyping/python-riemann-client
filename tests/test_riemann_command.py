from __future__ import absolute_import

import re
import socket

import click.testing

import riemann_client.command


def run_cli(args):
    args = [u'-T', u'none'] + list(args)
    runner = click.testing.CliRunner()
    result = runner.invoke(riemann_client.command.main, args)
    assert result.exit_code == 0
    return result


def strip(string):
    return re.sub(u'\s+', u'', string)


def assert_output_eq(args, expected):
    assert strip(run_cli(args).output) == strip(expected)


def test_send_empty_message():
    assert_output_eq([u'send'], u'{"host": "%s"}' % socket.gethostname())


POPULATED_MESSAGE = u"""{
  "attributes": {
    "key": "value"
  },
  "description": "description",
  "host": "%s",
  "metric_f": 11.5,
  "service": "service",
  "state": "state",
  "tags": [
    "tag"
  ],
  "time": 1408030991,
  "ttl": 120.5
}
""" % socket.gethostname()


def test_send():
    assert_output_eq([
        u'send',
        u'--attribute', u'key=value',
        u'--description', u'description',
        u'--metric_f', u'11.5',
        u'--service', u'service',
        u'--state', u'state',
        u'--tag', u'tag',
        u'--time', u'1408030991',
        u'--ttl', u'120.5'
    ], POPULATED_MESSAGE)


def test_send_short():
    assert_output_eq([
        u'send',
        u'-a', u'key=value',
        u'-d', u'description',
        u'-m', u'11.5',
        u'-s', u'service',
        u'-S', u'state',
        u'-t', u'tag',
        u'-T', u'1408030991',
        u'-l', u'120.5'
    ], POPULATED_MESSAGE)


def test_send_noecho():
    assert_output_eq([
        'send',
        '--attribute', 'key=value',
        '--description', 'description',
        '--metric_f', '11.5',
        '--service', 'service',
        '--state', 'state',
        '--tag', 'tag',
        '--time', '1408030991',
        '--ttl', '120.5',
        '--no-echo'
    ], '')


def test_query():
    assert_output_eq([u'query', u'true'], u'[]')
