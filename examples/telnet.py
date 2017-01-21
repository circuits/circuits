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
from __future__ import print_function

import os
from optparse import OptionParser

import circuits
from circuits import Component, handler
from circuits.io import stdin
from circuits.net.events import connect, write
from circuits.net.sockets import TCPClient, UDPClient, UNIXClient
from circuits.tools import graph

USAGE = "%prog [options] host [port]"
VERSION = "%prog v" + circuits.__version__


def parse_options():
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.add_option(
        "-s", "--secure",
        action="store_true", default=False, dest="secure",
        help="Enable secure mode"
    )

    parser.add_option(
        "-u", "--udp",
        action="store_true", default=False, dest="udp",
        help="Use UDP transport",
    )

    parser.add_option(
        "-v", "--verbose",
        action="store_true", default=False, dest="verbose",
        help="Enable verbose debugging",
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

    def __init__(self, *args, **opts):
        super(Telnet, self).__init__()

        self.args = args
        self.opts = opts

        if len(args) == 1:
            if os.path.exists(args[0]):
                UNIXClient(channel=self.channel).register(self)
                host = dest = port = args[0]
                dest = (dest,)
            else:
                raise OSError("Path %s not found" % args[0])
        else:
            if not opts["udp"]:
                TCPClient(channel=self.channel).register(self)
            else:
                UDPClient(0, channel=self.channel).register(self)

            host, port = args
            port = int(port)
            dest = host, port

        self.host = host
        self.port = port

        print("Trying %s ..." % host)

        if not opts["udp"]:
            self.fire(connect(*dest, secure=opts["secure"]))
        else:
            self.fire(write((host, port), b"\x00"))

    def ready(self, *args):
        graph(self.root)

    def connected(self, host, port=None):
        """connected Event Handler

        This event is fired by the TCPClient Componentt to indicate a
        successful connection.
        """

        print("connected to {0}".format(host))

    def error(self, *args, **kwargs):
        """error Event Handler

        If any exception/error occurs in the system this event is triggered.
        """

        if len(args) == 3:
            print("ERROR: {0}".format(args[1]))
        else:
            print("ERROR: {0}".format(args[0]))

    def read(self, *args):
        """read Event Handler

        This event is fired by the underlying TCPClient Component when there
        is data to be read from the connection.
        """

        if len(args) == 1:
            data = args[0]
        else:
            peer, data = args

        data = data.strip().decode("utf-8")

        print(data)

    # Setup an Event Handler for "read" events on the "stdin" channel.
    @handler("read", channel="stdin")
    def _on_stdin_read(self, data):
        """read Event Handler for stdin

        This event is triggered by the connected ``stdin`` component when
        there is new data to be read in from standard input.
        """

        if not self.opts["udp"]:
            self.fire(write(data))
        else:
            self.fire(write((self.host, self.port), data))


def main():
    opts, args = parse_options()

    # Configure and "run" the System.
    app = Telnet(*args, **opts.__dict__)
    if opts.verbose:
        from circuits import Debugger
        Debugger().register(app)
    stdin.register(app)
    app.run()


if __name__ == "__main__":
    main()
