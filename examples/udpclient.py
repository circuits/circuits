#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) UDP Client

A trivial simple example of using circuits to build a simple
UDP Socket Client.

This example demonstrates:
    * Basic Component creation.
    * Basic Event handling.
    * Basic Networking

This example makes use of:
    * Component
    * Event
    * Manager
    * net.sockets.UDPClient
"""

import optparse

from circuits import handler
from circuits.io import stdin
from circuits.net.sockets import UDPClient
from circuits import __version__ as systemVersion

USAGE = "%prog [options] address:[port]"
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

    parser.add_option("-b", "--bind",
            action="store", type="str", default="0.0.0.0:8000", dest="bind",
            help="Bind to address:[port]")

    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit, 1

    return opts, args

###
### Components
###

class Client(UDPClient):

    def __init__(self, bind, dest):
        super(Client, self).__init__(bind)

        self.dest = dest

    def read(self, address, data):
        print "%r: %r" % (address, data.strip())

    @handler("read", target="stdin")
    def stdin_read(self, data):
        self.write(self.dest, data)

###
### Main
###

def main():
    opts, args = parse_options()

    if ":" in opts.bind:
        address, port = opts.bind.split(":")
        bind = address, int(port)
    else:
        bind = opts.bind, 8000

    if ":" in args[0]:
        dest = args[0].split(":")
        dest = dest[0], int(dest[1])
    else:
        dest = args[0], 8000

    (Client(bind, dest=dest) + stdin).run()

###
### Entry Point
###

if __name__ == "__main__":
    main()
