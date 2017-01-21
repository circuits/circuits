#!/usr/bin/env python
"""Node Server Example

This example demonstrates how to create a very simple node server
that supports bi-diractional messaging between server and connected
clients forming a cluster of nodes.
"""
from __future__ import print_function

from optparse import OptionParser
from os import getpid

from circuits import Component, Debugger
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
        """Initialize our ``ChatServer`` Component.

        This uses the convenience ``init`` method which is called after the
        component is proeprly constructed and initialized and passed the
        same args and kwargs that were passed during construction.
        """

        self.args = args
        self.opts = opts

        self.clients = {}

        if opts.debug:
            Debugger().register(self)

        if ":" in opts.bind:
            address, port = opts.bind.split(":")
            port = int(port)
        else:
            address, port = opts.bind, 8000

        Node(port=port, server_ip=address).register(self)

    def connect(self, sock, host, port):
        """Connect Event -- Triggered for new connecting clients"""

        self.clients[sock] = {
            "host": sock,
            "port": port,
        }

    def disconnect(self, sock):
        """Disconnect Event -- Triggered for disconnecting clients"""

        if sock not in self.clients:
            return

        del self.clients[sock]

    def ready(self, server, bind):
        print("Ready! Listening on {}:{}".format(*bind))
        print("Waiting for remote events...")

    def hello(self):
        return "Hello World! ({0:d})".format(getpid())


def main():
    opts, args = parse_options()

    # Configure and "run" the System.
    NodeServer(args, opts).run()


if __name__ == "__main__":
    main()
