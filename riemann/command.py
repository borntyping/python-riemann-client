"""Riemann command line client"""

from __future__ import absolute_import, print_function

import argparse

import riemann.client
import riemann.transport

TRANSPORT_CLASSES = {
    'udp': riemann.transport.UDPTransport,
    'tcp': riemann.transport.TCPTransport
}


def wide_formatter(*args, **kwargs):
    kwargs.setdefault('max_help_position', 32)
    kwargs.setdefault('width', 96)
    return argparse.HelpFormatter(*args, **kwargs)

parser = argparse.ArgumentParser(
    formatter_class=wide_formatter, description=(
        "Uses the RIEMANN_HOST and RIEMANN_PORT environment variables "
        "if no host and port are given. If they are not set, the transports "
        "will use a default host and port of localhost:5555."))
parser.add_argument(
    '-v', '--version', action='version',
    version='python-riemann-client v{version} by {author}'.format(
        version=riemann.__version__,
        author=riemann.__author__),
    help="Show this program's version and exit")
parser.add_argument(
    'host', type=str, nargs='?', default=None,
    help="The hostname of a Riemann server (default: localhost)")
parser.add_argument(
    'port', type=int, nargs='?', default=None,
    help="The port to connect to the Riemann server on (default: 5555)")
parser.add_argument(
    '-t', '--transport', choices=TRANSPORT_CLASSES.keys(), default='tcp',
    help="The transport to use (default: %(default)s)")

subparsers = parser.add_subparsers(dest='subparser')

send = subparsers.add_parser(
    'send', formatter_class=wide_formatter,
    help='Send an event to Riemann')
send.add_argument(
    '-p', '--print', action='store_true', dest='print_message',
    help="Print the message that is sent to Riemann")

for arg_names, arg_type, arg_help in [
        (['-u', '--time'], int, "Unix timestamp"),
        (['-S', '--state'], str, "State"),
        (['-e', '--event-host'], str, "Host"),
        (['-D', '--description'], str, "Description"),
        (['-s', '--service'], str, "Service"),
        (['-T', '--tags'], list, "Tags"),
        (['-l', '--ttl'], int, "Time to live"),
        (['-m', '--metric'], float, "Value")]:
    send.add_argument(
        *arg_names, metavar=arg_type.__name__, type=arg_type, help=arg_help)


def filter_dict(function, dictionary):
    return dict((k, v) for k, v in dictionary.items() if function(k, v))


def send(args, client):
    client.event(**filter_dict(lambda k, v: v is not None, {
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


def main():
    args = parser.parse_args()
    transport = TRANSPORT_CLASSES[args.transport](args.host, args.port)
    with riemann.client.Client(transport=transport) as client:
        {'send': send}[args.subparser](args, client)
