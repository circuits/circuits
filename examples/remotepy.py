#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Remote Python

An example of using circuits and the event bdirge to create a server/client
system capable of executing remote python. In client mode, the user inputs
some arbitary python expression which is packaged up and sent as a remote
event across the event bridge to the server. The server processes and
computes the expression, packages up the result and sends it back across
the event bridge as an event.

This example demonstrates:
    * Basic Request/Response model using events.
    * Briding systems/components.

This example makes use of:
    * Component
    * Bridge
    * Manager
    * Stdin (lib)
"""

import optparse

import circuits
from circuits import io
from circuits.core import bridge
from circuits import handler, Event, Component, Debugger, Manager

USAGE = "%prog [options] [host[:port]]"
VERSION = "%prog v" + circuits.__version__

ERRORS = {}
ERRORS[0] = "Specify either server (-s/--server) mode or client (-c/--client mode"
ERRORS[1] = "Only specify one of either server (-s/--server) mode or client (-c/--client mode"

###
### Functions
###

def parse_options():
    """parse_options() -> opts, args

    Parse the command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-s", "--server",
            action="store_true", default=False, dest="server",
            help="Server mode")

    parser.add_option("-c", "--client",
            action="store_true", default=False, dest="client",
            help="Client mode")

    parser.add_option("-b", "--bind",
            action="store", type="string", default="0.0.0.0:8000", dest="bind",
            help="Bind to address:port")

    parser.add_option("-d", "--debug",
            action="store_true", default=False, dest="debug",
            help="Enable debug mode")

    opts, args = parser.parse_args()

    if not (opts.server or opts.client):
        print "ERROR: %s" % ERRORS[0]
        parser.print_help()
        raise SystemExit, 1
    elif opts.server and opts.client:
        print "ERROR: %s" % ERRORS[1]
        parser.print_help()
        raise SystemExit, 2

    return opts, args

###
### Events
###

class Result(Event): pass
class NewInput(Event): pass

###
### Components
###

class Input(Component):

    def __init__(self):
        super(Input, self).__init__()

        self.push(io.Write(">>> "), "write", "stdout")

    @handler("read", target="stdin")
    def read(self, data):
        self.push(NewInput(data.strip()), "newinput")
        self.push(io.Write(">>> "), "write", "stdout")

class Calc(Component):

    def result(self, r):
        self.push(io.Write("%s\n" % r), "write", "stdout")

class Adder(Component):

    def newinput(self, s):
        r = eval(s)
        self.push(Result(r), "result")

###
### Main
###

def main():
    opts, args = parse_options()

    if ":" in opts.bind:
        address, port = opts.bind.split(":", 1)
        bind = (address, int(port))
    else:
        bind = (opts.bind, 8000)

    nodes = []
    for arg in args:
        if ":" in arg:
            address, port = arg.split(":", 1)
            port = int(port)
        else:
            address, port = arg, bind[1]
        nodes.append((address, port))

    manager = Manager() + bridge.Bridge(nodes, bind=bind)

    if opts.debug:
        debugger = Debugger()
        debugger.IgnoreEvents.extend(
                [bridge.Read, bridge.Write, bridge.Error, bridge.Close,
                    io.Read, io.Write, io.Error])
        manager += debugger

    if opts.server:
        manager += Adder()
    elif opts.client:
        manager += io.stdin
        manager += io.stdout
        manager += Input()
        manager += Calc()

    manager.run()

###
### Entry Point
###

if __name__ == "__main__":
    main()
