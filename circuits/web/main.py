#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""Main

circutis.web Web Server and Testing Tool.
"""

import os
import optparse
from wsgiref.validate import validator
from wsgiref.simple_server import make_server

try:
    import hotshot
    import hotshot.stats
except ImportError:
    hostshot = None

try:
    import psyco
except ImportError:
    psyco = None

from circuits.core import workers
from circuits.net.pollers import Select
from circuits.tools import inspect, graph
from circuits import Component, Manager, Debugger
from circuits import __version__ as systemVersion
from circuits.web import BaseServer, Server, Controller, Static, wsgi

try:
    from circuits.net.pollers import Poll
except ImportError:
    Poll = None

try:
    from circuits.net.pollers import EPoll
except ImportError:
    EPoll = None


USAGE = "%prog [options] [docroot]"
VERSION = "%prog v" + systemVersion

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
            action="store", type="string", default="0.0.0.0:8000", dest="bind",
            help="Bind to address:[port]")

    parser.add_option("-j", "--jit",
            action="store_true", default=False, dest="jit",
            help="Use python HIT (psyco)")

    parser.add_option("-m", "--multiprocessing",
            action="store_true", default=False, dest="mp",
            help="Start in multiprocessing mode")

    parser.add_option("-t", "--type",
            action="store", type="string", default="select", dest="type",
            help="Specify type of poller to use")

    parser.add_option("-s", "--server",
            action="store", type="string", default="server", dest="server",
            help="Specify server to use")

    parser.add_option("-p", "--profile",
            action="store_true", default=False, dest="profile",
            help="Enable execution profiling support")

    parser.add_option("-d", "--debug",
            action="store_true", default=False, dest="debug",
            help="Enable debug mode")

    parser.add_option("-v", "--validate",
            action="store_true", default=False, dest="validate",
            help="Enable WSGI validation mode")

    opts, args = parser.parse_args()

    return opts, args

###
### Components
###

class HelloWorld(Component):

    channel = "web"

    def request(self, request, response):
        return "Hello World!"

class Root(Controller):

    def hello(self):
        return "Hello World!"

###
### Main
###

def main():
    opts, args = parse_options()

    if opts.jit and psyco:
        psyco.full()

    if ":" in opts.bind:
        address, port = opts.bind.split(":")
        port = int(port)
    else:
        address, port = opts.bind, 8000

    bind = (address, port)

    if opts.validate:
        application = (wsgi.Application() + Root())
        app = validator(application)

        httpd = make_server(address, port, app)
        httpd.serve_forever()
        
        raise SystemExit, 0

    manager = Manager()

    if opts.debug:
        manager += Debugger()

    poller = opts.type.lower()
    if poller == "poll":
        if Poll is None:
            print "No poll support available - defaulting to Select..."
            Poller = Select
        else:
            Poller = Poll
    elif poller == "epoll":
        if EPoll is None:
            print "No epoll support available - defaulting to Select..."
            Poller = Select
        else:
            Poller = EPoll
    else:
        Poller = Select

    if opts.server.lower() == "base":
        BaseServer(bind, poller=Poller).register(manager)
        HelloWorld().register(manager)
    else:
        Server(bind, poller=Poller).register(manager)
        Root().register(manager)

    docroot = os.getcwd() if not args else args[0]

    Static(docroot=docroot, dirlisting=True).register(manager)

    if opts.profile:
        if hotshot:
            profiler = hotshot.Profile(".profile")
            profiler.start()

    if opts.debug:
        print graph(manager, name="circuits.web")
        print
        print inspect(manager)

    if opts.mp and workers.HAS_MULTIPROCESSING:
        for i in xrange(workers.cpus() - 1):
            manager.start(process=True)
    else:
        print "No multiprocessing support available"

    manager.run()

    if opts.profile and hotshot:
        profiler.stop()
        profiler.close()

        stats = hotshot.stats.load(".profile")
        stats.strip_dirs()
        stats.sort_stats("time", "calls")
        stats.print_stats(20)

###
### Entry Point
###

if __name__ == "__main__":
    main()
