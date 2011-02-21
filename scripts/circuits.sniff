#!/usr/bin/env python

"""(Tool) Event Sniffer

Event sniffing tool. This tool can be used to sniff and debug Events as they
occur in another system. As long as that system has an instnace of the Bridge
Component, events can be sniffed and printed.
"""

import optparse

import circuits
from circuits import Debugger, Bridge, Manager

USAGE = "%prog [options] [host[:port]]"
VERSION = "%prog v" + circuits.__version__

###
### Functions
###

def parse_options():
    """parse_options() -> opts, args

    Parse the command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-b", "--bind",
            action="store", default="0.0.0.0:8000", dest="bind",
            help="Bind to address:port")

    opts, args = parser.parse_args()

    return opts, args

###
### Main
###

def main():
    opts, args = parse_options()

    if ":" in opts.bind:
        address, port = opts.bind.split(":")
        port = int(port)
    else:
        address, port = opts.bind, 8000

    if args:
        x = args[0].split(":")
        if len(x) > 1:
            nodes = [(x[0], int(x[1]))]
        else:
            nodes = [(x[0], 8000)]
    else:
        nodes = []

    manager = Manager()

    debugger = Debugger()
    debugger.IgnoreEvents.extend(["Read", "Write"])
    manager += debugger

    bridge = Bridge(port, address=address, nodes=nodes)
    manager += bridge

    manager.run()

###
### Entry Point
###

if __name__ == "__main__":
    main()
