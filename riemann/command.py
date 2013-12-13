"""Riemann command line client"""

from __future__ import absolute_import, print_function

import argparse
import os

import riemann.client

TRANSPORT_CLASSES = {
    'udp': riemann.client.UDPTransport,
    'tcp': riemann.client.TCPTransport
}


def wide_formatter(*args, **kwargs):
    kwargs.setdefault('max_help_position', 32)
    kwargs.setdefault('width', 96)
    return argparse.HelpFormatter(*args, **kwargs)

os.environ.setdefault('RIEMANN_HOST', 'localhost')
os.environ.setdefault('RIEMANN_PORT', '5555')

parser = argparse.ArgumentParser(formatter_class=wide_formatter)
parser.add_argument(
    '-v', '--version', action='version',
    version='python-riemann-client v{version} by {author}'.format(
        version=riemann.__version__,
        author=riemann.__author__),
    help="Show this program's version and exit")
parser.add_argument(
    'host', type=str, nargs='?', default=os.environ['RIEMANN_HOST'],
    help="The hostname of a Riemann server (env: %(default)s)")
parser.add_argument(
    'port', type=int, nargs='?', default=os.environ['RIEMANN_PORT'],
    help="The port to connect to the Riemann server on (env: %(default)s)")


subparsers = parser.add_subparsers()

send = subparsers.add_parser(
    'send', formatter_class=wide_formatter,
    help='Send an event to Riemann', conflict_handler='resolve')
send.add_argument(
    '-p', '--print', action='store_true', dest='print_message',
    help="Print the message that is sent to Riemann")
send.add_argument(
    '--transport', choices=TRANSPORT_CLASSES.keys(), default='tcp',
    help="The transport to use (default: %(default)s)")

for arg_names, arg_type, arg_help in [
        (['-u', '--time'], int, "Unix timestamp"),
        (['-S', '--state'], str, "Event state"),
        (['-e', '--event-host'], str, "Event host (defaults to the current host)"),
        (['-D', '--description'], str, "A description of the event"),
        (['-s', '--service'], str, "Event service"),
        (['-T', '--tags'], list, "Event tags"),
        (['-t', '--ttl'], int, "Event time to live"),
        (['-m', '--metric'], float, "Event metric value")]:
    send.add_argument(
        *arg_names, metavar=arg_type.__name__, type=arg_type, help=arg_help)


def filter_dict(function, dictionary):
    return dict((k, v) for k, v in dictionary.items() if function(k, v))


def main():
    args = parser.parse_args()
    transport = TRANSPORT_CLASSES[args.transport](args.host, args.port)
    with riemann.client.Client(transport=transport) as client:
        event = client.event(**filter_dict(lambda k, v: v is not None, {
            "time": args.time,
            "state": args.state,
            "host": args.event_host,
            "description": args.description,
            "service": args.service,
            "tags": args.tags,
            "ttl": args.ttl,
            "metric_f": args.metric
        }))

    if args.print_message:
        print(str(event).strip())
