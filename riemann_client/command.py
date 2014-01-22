"""Riemann command line client"""

from __future__ import absolute_import, print_function

import argparse
import json
import os

import riemann_client.client
import riemann_client.transport

TRANSPORT_CLASSES = {
    'udp': riemann_client.transport.UDPTransport,
    'tcp': riemann_client.transport.TCPTransport
}

parser = argparse.ArgumentParser(add_help=False, description=(
    "Uses the RIEMANN_HOST and RIEMANN_PORT environment variables "
    "if no host and port are given. If they are not set, the transports "
    "will use a default host and port of localhost:5555."))

parser.add_argument(
    '-h', '--help', action='help',
    help="show this help message and exit")

parser.add_argument(
    '-v', '--version', action='version',
    version='python-riemann-client v{version} by {author}'.format(
        version=riemann_client.__version__,
        author=riemann_client.__author__),
    help="Show this program's version and exit")

parser.add_argument(
    '-H', '--host', type=str,
    default=os.environ.get('RIEMANN_HOST', 'localhost'),
    help="The hostname of a Riemann server (environ: %(default)s)")

parser.add_argument(
    '-P', '--port', type=int,
    default=os.environ.get('RIEMANN_PORT', 5555),
    help="The port to connect to the Riemann server on (environ: %(default)s)")

parser.add_argument(
    '-t', '--transport', choices=TRANSPORT_CLASSES.keys(), default='tcp',
    help="The transport to use (default: %(default)s)")

subparsers = parser.add_subparsers(dest='subparser')


def send_function(args, client):
    """Sends a single command to Riemann"""
    event = client.event(
        time=args.time,
        state=args.state,
        host=args.host,
        description=args.description,
        service=args.service,
        tags=args.tags,
        ttl=args.ttl,
        metric_f=args.metric)

    if args.print_message:
        print(str(event).strip())

send = subparsers.add_parser('send', help='Send an event to Riemann')

send.add_argument(
    '-p', '--print', action='store_true', dest='print_message',
    help="Print the message that is sent to Riemann")

send_arguments = [
    (['-u', '--time'], int, "Unix timestamp"),
    (['-S', '--state'], str, "State"),
    (['-e', '--event-host'], str, "Host"),
    (['-D', '--description'], str, "Description"),
    (['-s', '--service'], str, "Service"),
    (['-T', '--tags'], list, "Tags"),
    (['-l', '--ttl'], int, "Time to live"),
    (['-m', '--metric'], float, "Value")]

for flags, atype, ahelp in send_arguments:
    send.add_argument(*flags, metavar=atype.__name__, type=atype, help=ahelp)

send.set_defaults(function=send_function)


def query_function(args, client):
    """Queries the Riemann index and outputs the returned events as JSON

    UDP is not supported when querying"""
    print(json.dumps(client.query(args.query), sort_keys=True, indent=2))

query = subparsers.add_parser('query', help='Query the Riemann index')
query.add_argument('query', type=str, help="The query to send")
query.set_defaults(function=query_function)


def main():
    args = parser.parse_args()

    transport_class = TRANSPORT_CLASSES[args.transport]
    transport = transport_class(args.host, args.port)

    with riemann_client.client.Client(transport=transport) as client:
        args.function(args, client)
