#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Telnet Client

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
    * lib.sockets.TCPClient
"""

import optparse

from circuits.lib.io import stdin
from circuits import handler, Component
from circuits import __version__ as systemVersion
from circuits.lib.sockets import TCPClient, Connect, Write

USAGE = "%prog [options] host [port]"
VERSION = "%prog v" + systemVersion

###
### Functions
###

def parse_options():
    """parse_options() -> opts, args

    Parse any command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-s", "--ssl",
            action="store_true", default=False, dest="ssl",
            help="Enable Secure Socket Layer (SSL)")

    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit, 1

    return opts, args

###
### Components
###

class Telnet(Component):

    channel = "telnet"

    def __init__(self, host, port):
        super(Telnet, self).__init__()

        self += TCPClient(channel=self.channel)
        self.push(Connect(host, port), "connect")

    def connected(self, host, port):
        print "Connected to %s" % host

    def error(self, e):
        print "ERROR: %r" % e

    def read(self, data):
        print data.strip()

    @handler("read", target="stdin")
    def stdin_read(self, data):
        self.push(Write(data), "write")

###
### Main
###

def main():
    opts, args = parse_options()

    host = args[0]
    if len(args) > 1:
        port = int(args[1])
    else:
        port = 23

    print "Trying %s..." % host

    (Telnet(host, port) + stdin).run()

###
### Entry Point
###

if __name__ == "__main__":
    main()
