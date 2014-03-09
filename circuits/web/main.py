#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Main

circutis.web Web Server and Testing Tool.
"""

import os
from sys import stderr
from optparse import OptionParser
from wsgiref.validate import validator
from wsgiref.simple_server import make_server

try:
    import hotshot
    import hotshot.stats
except ImportError:
    hostshot = None

try:
    import psyco
except:
    psyco = None  # NOQA

from circuits.core.pollers import Select
from circuits.tools import inspect, graph
from circuits import Component, Manager, Debugger
from circuits import __version__ as systemVersion

from circuits.web.wsgi import Application
from circuits.web import BaseServer, Controller, Logger, Server, Static

try:
    from circuits.core.pollers import Poll
except ImportError:
    Poll = None  # NOQA

try:
    from circuits.core.pollers import EPoll
except ImportError:
    EPoll = None  # NOQA


USAGE = "%prog [options] [docroot]"
VERSION = "%prog v" + systemVersion


def parse_options():
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.add_option(
        "-b", "--bind",
        action="store", type="string", default="0.0.0.0:8000", dest="bind",
        help="Bind to address:[port]"
    )

    parser.add_option(
        "-l", "--logging",
        action="store_true", default=False, dest="logging",
        help="Enable access logs"
    )

    if psyco is not None:
        parser.add_option(
            "-j", "--jit",
            action="store_true", default=False, dest="jit",
            help="Use python HIT (psyco)"
        )

    parser.add_option(
        "-m", "--multiprocessing",
        action="store", type="int", default=0, dest="mp",
        help="Specify no. of processes to start (multiprocessing)"
    )

    parser.add_option(
        "-t", "--type",
        action="store", type="string", default="select", dest="type",
        help="Specify type of poller to use"
    )

    parser.add_option(
        "-s", "--server",
        action="store", type="string", default="server", dest="server",
        help="Specify server to use"
    )

    parser.add_option(
        "-p", "--profile",
        action="store_true", default=False, dest="profile",
        help="Enable execution profiling support"
    )

    parser.add_option(
        "-d", "--debug",
        action="store_true", default=False, dest="debug",
        help="Enable debug mode"
    )

    parser.add_option(
        "-v", "--validate",
        action="store_true", default=False, dest="validate",
        help="Enable WSGI validation mode"
    )

    opts, args = parser.parse_args()

    return opts, args


class HelloWorld(Component):

    channel = "web"

    def request(self, request, response):
        return "Hello World!"


class Root(Controller):

    def hello(self):
        return "Hello World!"


def main():
    opts, args = parse_options()

    if psyco and opts.jit:
        psyco.full()

    if ":" in opts.bind:
        address, port = opts.bind.split(":")
        port = int(port)
    else:
        address, port = opts.bind, 8000

    bind = (address, port)

    if opts.validate:
        application = (Application() + Root())
        app = validator(application)

        httpd = make_server(address, port, app)
        httpd.serve_forever()

        raise SystemExit(0)

    manager = Manager()

    if opts.debug:
        manager += Debugger()

    poller = opts.type.lower()
    if poller == "poll":
        if Poll is None:
            stderr.write("No poll support available - defaulting to Select...")
            Poller = Select
        else:
            Poller = Poll
    elif poller == "epoll":
        if EPoll is None:
            stderr.write("No epoll support available - defaulting to Select...")
            Poller = Select
        else:
            Poller = EPoll
    else:
        Poller = Select

    Poller().register(manager)

    if opts.server.lower() == "base":
        BaseServer(bind).register(manager)
        HelloWorld().register(manager)
    else:
        Server(bind).register(manager)
        Root().register(manager)

    docroot = os.getcwd() if not args else args[0]

    Static(docroot=docroot, dirlisting=True).register(manager)

    if opts.logging:
        Logger().register(manager)

    if opts.profile and hotshot:
        profiler = hotshot.Profile(".profile")
        profiler.start()

    if opts.debug:
        print(graph(manager, name="circuits.web"))
        print()
        print(inspect(manager))

    for i in range(opts.mp):
        manager.start(process=True)

    manager.run()

    if opts.profile and hotshot:
        profiler.stop()
        profiler.close()

        stats = hotshot.stats.load(".profile")
        stats.strip_dirs()
        stats.sort_stats("time", "calls")
        stats.print_stats(20)


if __name__ == "__main__":
    main()
