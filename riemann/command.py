"""Riemann command line client"""

from __future__ import absolute_import, unicode_literals, print_function

import argparse

import riemann.client


def wide_formatter(*args, **kwargs):
    kwargs.setdefault('max_help_position', 32)
    kwargs.setdefault('width', 96)
    return argparse.HelpFormatter(*args, **kwargs)


parser = argparse.ArgumentParser(formatter_class=wide_formatter)
parser.add_argument(
    '-v', '--version', action='version',
    version='python-riemann-client v{version} by {author}'.format(
        version=riemann.__version__,
        author=riemann.__author__),
    help="Show this program's version and exit")
parser.add_argument(
    'host', type=str, nargs='?', default='localhost',
    help="The hostname of a Riemann server")
parser.add_argument(
    'port', type=int, nargs='?', default=5555,
    help="The port to connect to the Riemann server on")


subparsers = parser.add_subparsers()

send = subparsers.add_parser(
    'send', formatter_class=wide_formatter,
    help='Send an event to Riemann')
send.add_argument(
    '-p', '--print', action='store_true', dest='print_message',
    help="Print the message that is sent to Riemann")

for arg_names, arg_type, arg_help in [
        (['-u', '--time'], int, "Unix timestamp"),
        (['-S', '--state'], str, "Event state"),
        (['-H', '--host'], str, "Event host (defaults to the current host)"),
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

    with riemann.client.UDPClient(host=args.host, port=args.port) as client:
        client.event(args.service, **filter_dict(lambda k, v: v is not None, {
            "time": args.time,
            "state": args.state,
            "host": args.host,
            "description": args.description,
            "tags": args.tags,
            "ttl": args.ttl,
            "metric_f": args.metric
        }))
        if args.print_message:
            print(str(client.next).strip())
        client.send_next_message()
