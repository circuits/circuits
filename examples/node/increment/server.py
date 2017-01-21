#!/usr/bin/env python
from optparse import OptionParser

from circuits import Component, Debugger, handler
from circuits.node import Node

__version__ = "0.0.1"

USAGE = "%prog [options]"
VERSION = "%prog v" + __version__


def parse_options():
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.add_option(
        "-b", "--bind",
        action="store", type="string",
        default="0.0.0.0:8000", dest="bind",
        help="Bind to address:[port]"
    )

    parser.add_option(
        "-d", "--debug",
        action="store_true",
        default=False, dest="debug",
        help="Enable debug mode"
    )

    opts, args = parser.parse_args()

    return opts, args


class NodeServer(Component):

    def init(self, args, opts):
        if opts.debug:
            Debugger().register(self)

        if ":" in opts.bind:
            address, port = opts.bind.split(":")
            port = int(port)
        else:
            address, port = opts.bind, 8000

        Node(port=port, server_ip=address).register(self)

    def connect(self, sock, host, port):
        print('Peer connected: %s:%d' % (host, port))

    def disconnect(self, sock):
        print('Peer disconnected: %s' % sock)

    def ready(self, server, bind):
        print('Server ready: %s:%d' % bind)

    @handler('increment')
    def increment(self, value):
        print('Execute increment event (value: %d)' % value)
        return value + 1


def main():
    opts, args = parse_options()

    # Configure and "run" the System.
    NodeServer(args, opts).run()


if __name__ == "__main__":
    main()
