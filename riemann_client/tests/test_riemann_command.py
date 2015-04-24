from __future__ import absolute_import, unicode_literals

import re
import socket

import click.testing

import riemann_client.command


def run_cli(args):
    args = ['-T', 'none'] + list(args)
    runner = click.testing.CliRunner()
    result = runner.invoke(riemann_client.command.main, args)
    assert result.exit_code == 0
    return result


def strip(string):
    return re.sub('\s+', '', string)


def assert_output_eq(args, expected):
    assert strip(run_cli(args).output) == strip(expected)


def test_send_empty_message():
    assert_output_eq(['send'], '{"host": "%s"}' % socket.gethostname())


POPULATED_MESSAGE = """{
  "attributes": {
    "key": "value"
  },
  "description": "description",
  "host": "%s",
  "metric_f": 11.1,
  "service": "service",
  "state": "state",
  "tags": [
    "tag"
  ],
  "time": 1408030991,
  "ttl": 120
}
""" % socket.gethostname()


def test_send():
    assert_output_eq([
        'send',
        '--attribute', 'key=value',
        '--description', 'description',
        '--metric_f', '11.1',
        '--service', 'service',
        '--state', 'state',
        '--tag', 'tag',
        '--time', '1408030991',
        '--ttl', '120'
    ], POPULATED_MESSAGE)


def test_send_short():
    assert_output_eq([
        'send',
        '-a', 'key=value',
        '-d', 'description',
        '-m', '11.1',
        '-s', 'service',
        '-S', 'state',
        '-t', 'tag',
        '-T', '1408030991',
        '-l', '120'
    ], POPULATED_MESSAGE)


def test_query():
    assert_output_eq(['query', 'true'], '[]')
