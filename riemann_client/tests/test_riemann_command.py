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


def strip_whitespace(string):
    return re.sub('\s+', '', string)


def compare_output(args, expected):
    output = strip_whitespace(run_cli(args).output)
    expected_output = strip_whitespace(expected)
    return output == expected_output


EMPTY_MESSAGE = """{
  "attributes": {},
  "description": "",
  "host": "%s",
  "metric_d": 0,
  "metric_f": 0,
  "metric_sint64": 0,
  "service": "",
  "state": "",
  "tags": [],
  "time": 0,
  "ttl": 0
}
"""


def test_send_blank():
    assert compare_output(['send'], EMPTY_MESSAGE % socket.gethostname())


POPULATED_MESSAGE = """{
  "attributes": {
    "key": "value"
  },
  "description": "description",
  "host": "%s",
  "metric_d": 0,
  "metric_f": 11.1,
  "metric_sint64": 0,
  "service": "service",
  "state": "state",
  "tags": [
    "tag"
  ],
  "time": 1408030991,
  "ttl": 120
}
"""


def test_send():
    assert compare_output([
        'send',
        '--attribute', 'key=value',
        '--description', 'description',
        '--metric_f', '11.1',
        '--service', 'service',
        '--state', 'state',
        '--tag', 'tag',
        '--time', '1408030991',
        '--ttl', '120'
    ], POPULATED_MESSAGE % socket.gethostname())


def test_send_short():
    assert compare_output([
        'send',
        '-a', 'key=value',
        '-d', 'description',
        '-m', '11.1',
        '-s', 'service',
        '-S', 'state',
        '-t', 'tag',
        '-T', '1408030991',
        '-l', '120'
    ], POPULATED_MESSAGE % socket.gethostname())


def test_query():
    assert compare_output(['query', 'true'], '[]')
