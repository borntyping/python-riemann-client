"""Riemann command line client"""

from __future__ import absolute_import, print_function

import json
import sys

import click

import riemann_client
import riemann_client.client
import riemann_client.transport

__all__ = ['main']


class CommandLineClient(riemann_client.client.Client):
    """Prints to STDERR when an error message is recived from Riemann"""

    def __exit__(self, exc_type, exc_value, traceback):
        super(CommandLineClient, self).__exit__(exc_type, exc_value, traceback)

        if isinstance(exc_type, riemann_client.transport.RiemannError):
            click.echo("The server responded with an error: {0}".format(
                exc_value.message), file=sys.stderr)
            exit(1)


class Pair(click.ParamType):
    """A key value parameter seperated with an '=' symbol"""
    name = 'pair'

    def convert(self, value, param, ctx):
        key, value = value.split('=', 1)
        return key.strip(), value.strip()


def echo(data):
    """Echo a json dump of an object using click"""
    return click.echo(json.dumps(data, sort_keys=True, indent=2))


@click.group()
@click.version_option(version=riemann_client.__version__)
@click.option('--host', '-H', type=click.STRING, default='localhost',
              envvar='RIEMANN_HOST', help='Riemann server hostname.')
@click.option('--port', '-P', type=click.INT, default=5555,
              envvar='RIEMANN_PORT', help='Riemann server port.')
@click.option('--transport', '-T', 'transport_type', default='tcp',
              type=click.Choice(['udp', 'tcp', 'tls', 'none']),
              help='The protocol to use to connect to Riemann.')
@click.option('--timeout', '-I', type=click.FLOAT, default=None,
              help='Timeout for TCP based connections.')
@click.option('--ca-certs', '-C', type=click.Path(),
              help='A CA certificate bundle for TLS connections.')
@click.pass_context
def main(ctx, host, port, transport_type, timeout, ca_certs):
    """Connects to a Riemann server to send events or query the index

    By default, will attempt to contact Riemann on localhost:5555 over TCP. The
    RIEMANN_HOST and RIEMANN_PORT environment variables can be used to
    configure the host and port used. Command line parameters will override the
    environment variables.

    Use `-T none` to test commands without actually connecting to a server.
    """
    if transport_type == 'udp':
        if timeout is not None:
            ctx.fail('--timeout cannot be used with the UDP transport')
        transport = riemann_client.transport.UDPTransport(host, port)
    elif transport_type == 'tcp':
        transport = riemann_client.transport.TCPTransport(host, port, timeout)
    elif transport_type == 'tls':
        if ca_certs is None:
            ctx.fail('--ca-certs must be set when using the TLS transport')
        transport = riemann_client.transport.TLSTransport(
            host, port, timeout, ca_certs)
    elif transport_type == 'none':
        transport = riemann_client.transport.BlankTransport()

    ctx.obj = transport


@main.command()
@click.option('-T', '--time', type=click.INT,
              help="Event timestamp (unix format)")
@click.option('-S', '--state', type=click.STRING,
              help="Event state")
@click.option('-s', '--service', type=click.STRING,
              help="Event service name")
@click.option('-h', '--host', type=click.STRING,
              help="Event hostname (uses system's by default)")
@click.option('-d', '--description', type=click.STRING,
              help="Event description")
@click.option('-t', '--tag', type=click.STRING, multiple=True,
              help="Event tag (multiple)")
@click.option('-l', '--ttl', type=click.INT,
              help="Event time to live in seconds")
@click.option('-a', '--attr', '--attribute', type=Pair(), multiple=True,
              help="Event attribute (key=value, multiple)")
@click.option('-m', '--metric', '--metric_f', type=click.FLOAT,
              help="Event metric (uses metric_f)")
@click.pass_obj
def send(transport, time, state, host, description, service, tag, attribute,
         ttl, metric_f):
    """Send a single event to Riemann"""
    client = CommandLineClient(transport)
    event = client.create_event({
        'time': time,
        'state': state,
        'host': host,
        'description': description,
        'service': service,
        'tags': tag,
        'attributes': dict(attribute),
        'ttl': ttl,
        'metric_f': metric_f
    })

    with client:
        client.send_event(event)

    echo(client.create_dict(event))


@main.command()
@click.argument('query', 'query')
@click.pass_obj
def query(transport, query):
    """Query the Riemann server"""
    with CommandLineClient(transport) as client:
        echo(client.query(query))
