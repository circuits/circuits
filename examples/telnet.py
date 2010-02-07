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

import os
import optparse
from socket import gethostname

from circuits.io import stdin
from circuits import handler, Component
from circuits import __version__ as systemVersion
from circuits.net.sockets import TCPClient, UNIXClient, Connect, Write

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

    def __init__(self, *args):
        super(Telnet, self).__init__()

        if len(args) == 1:
            if os.path.exists(args[0]):
                self += UNIXClient(channel=self.channel)
                host = dest = port = args[0]
                dest = (dest,)
            else:
                raise OSError("Path %s not found" % args[0])
        else:
            self += TCPClient(channel=self.channel)
            host, port = args
            port = int(port)
            dest = host, port

        print "Trying %s ..." % host
        self.push(Connect(*dest), "connect")

    def connected(self, host, port=None):
        print "Connected to %s" % host

    def error(self, *args):
        if len(args) == 3:
            type, value, traceback = args
        else:
            value = args[0]
            type = type(value)
            traceback = None

        print "ERROR: %s" % value

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

    (Telnet(*args) + stdin).run()

###
### Entry Point
###

if __name__ == "__main__":
    main()
