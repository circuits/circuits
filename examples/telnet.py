#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Telnet Example

A basic telnet-like clone that connects to remote hosts
via tcp and allows the user to send data to the remote
server.

This example demonstrates:
    * Basic Component creation.
    * Basic Event handling.
    * Basiv Networking
    * Basic Request/Response Networking

This example makes use of:
    * Component
    * Event
    * net.sockets.TCPClient
"""

import os
from optparse import OptionParser

from circuits.io import stdin
from circuits import handler, Component
from circuits import __version__ as systemVersion
from circuits.net.sockets import TCPClient, UNIXClient, Connect, Write

USAGE = "%prog [options] host [port]"
VERSION = "%prog v" + systemVersion


def parse_options():
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.add_option(
        "-s", "--ssl",
        action="store_true", default=False, dest="ssl",
        help="Enable Secure Socket Layer (SSL)"
    )

    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit(1)

    return opts, args


class Telnet(Component):

    # Define a separate channel for this component so we don't clash with
    # the ``read`` event of the ``stdin`` component.
    channel = "telnet"

    def __init__(self, *args):
        super(Telnet, self).__init__()

        if len(args) == 1:
            if os.path.exists(args[0]):
                UNIXClient(channel=self.channel).register(self)
                host = dest = port = args[0]
                dest = (dest,)
            else:
                raise OSError("Path %s not found" % args[0])
        else:
            TCPClient(channel=self.channel).register(self)
            host, port = args
            port = int(port)
            dest = host, port

        print("Trying %s ..." % host)
        self.fire(Connect(*dest))

    def connected(self, host, port=None):
        """Connected Event Handler

        This event is fired by the TCPClient Componentt to indicate a
        successful connection.
        """

        print("Connected to {0}".format(host))

    def error(self, *args, **kwargs):
        """Error Event Handler

        If any exception/error occurs in the system this event is triggered.
        """

        if len(args) == 3:
            print("ERROR: {0}".format(args[1]))
        else:
            print("ERROR: {0}".format(args[0]))

    def read(self, data):
        """Read Event Handler

        This event is fired by the underlying TCPClient Component when there
        is data to be read from the connection.
        """

        print(data.strip())

    # Setup an Event Handler for "read" events on the "stdin" channel.
    @handler("read", channel="stdin")
    def _on_stdin_read(self, data):
        """Read Event Handler for stdin

        This event is triggered by the connected ``stdin`` component when
        there is new data to be read in from standard input.
        """

        self.fire(Write(data))


def main():
    opts, args = parse_options()

    # Configure and "run" the System.
    app = Telnet(*args)
    stdin.register(app)
    app.run()


if __name__ == "__main__":
    main()
