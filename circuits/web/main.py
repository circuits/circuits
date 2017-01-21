#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main

circutis.web Web Server and Testing Tool.
"""
import os
from hashlib import md5
from optparse import OptionParser
from sys import stderr
from wsgiref.simple_server import make_server
from wsgiref.validate import validator

import circuits
from circuits import Component, Debugger, Manager, handler
from circuits.core.pollers import Select
from circuits.tools import graph, inspect
from circuits.web import BaseServer, Controller, Logger, Server, Static
from circuits.web.tools import check_auth, digest_auth
from circuits.web.wsgi import Application

try:
    import hotshot
    import hotshot.stats
except ImportError:
    hostshot = None


try:
    from circuits.core.pollers import Poll
except ImportError:
    Poll = None  # NOQA

try:
    from circuits.core.pollers import EPoll
except ImportError:
    EPoll = None  # NOQA


USAGE = "%prog [options] [docroot]"
VERSION = "%prog v" + circuits.__version__


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
        help="Enable logging of requests"
    )

    parser.add_option(
        "-p", "--passwd",
        action="store", default=None, dest="passwd",
        help="Location to passwd file for Digest Auth"
    )

    parser.add_option(
        "-j", "--jobs",
        action="store", type="int", default=0, dest="jobs",
        help="Specify no. of jobs/processes to start"
    )

    parser.add_option(
        "", "--poller",
        action="store", type="string", default="select", dest="poller",
        help="Specify type of poller to use"
    )

    parser.add_option(
        "", "--server",
        action="store", type="string", default="server", dest="server",
        help="Specify server to use"
    )

    parser.add_option(
        "", "--profile",
        action="store_true", default=False, dest="profile",
        help="Enable execution profiling support"
    )

    parser.add_option(
        "", "--debug",
        action="store_true", default=False, dest="debug",
        help="Enable debug mode"
    )

    parser.add_option(
        "", "--validate",
        action="store_true", default=False, dest="validate",
        help="Enable WSGI validation mode"
    )

    opts, args = parser.parse_args()

    return opts, args


class Authentication(Component):

    channel = "web"

    realm = "Secure Area"
    users = {"admin": md5("admin").hexdigest()}

    def __init__(self, channel=channel, realm=None, passwd=None):
        super(Authentication, self).__init__(self, channel=channel)

        if realm is not None:
            self.realm = realm

        if passwd is not None:
            with open(passwd, "r") as f:
                lines = (line.strip() for line in f)
                self.users = dict((line.split(":", 1) for line in lines))

    @handler("request", priority=10)
    def request(self, event, request, response):
        if not check_auth(request, response, self.realm, self.users):
            event.stop()
            return digest_auth(request, response, self.realm, self.users)


class HelloWorld(Component):

    channel = "web"

    def request(self, request, response):
        return "Hello World!"


class Root(Controller):

    def hello(self):
        return "Hello World!"


def select_poller(poller):
    if poller == "poll":
        if Poll is None:
            stderr.write(
                "No poll support available - defaulting to Select..."
            )
            Poller = Select
        else:
            Poller = Poll
    elif poller == "epoll":
        if EPoll is None:
            stderr.write(
                "No epoll support available - defaulting to Select..."
            )
            Poller = Select
        else:
            Poller = EPoll
    else:
        Poller = Select

    return Poller


def parse_bind(bind):
    if ":" in bind:
        address, port = bind.split(":")
        port = int(port)
    else:
        address, port = bind, 8000

    return (address, port)


def main():
    opts, args = parse_options()

    bind = parse_bind(opts.bind)

    if opts.validate:
        application = (Application() + Root())
        app = validator(application)

        httpd = make_server(bind[0], bind[1], app)
        httpd.serve_forever()

        raise SystemExit(0)

    manager = Manager()

    opts.debug and Debugger().register(manager)

    Poller = select_poller(opts.poller.lower())
    Poller().register(manager)

    if opts.server.lower() == "base":
        BaseServer(bind).register(manager)
        HelloWorld().register(manager)
    else:
        Server(bind).register(manager)
        Root().register(manager)

    docroot = os.getcwd() if not args else args[0]

    Static(docroot=docroot, dirlisting=True).register(manager)

    opts.passwd and Authentication(passwd=opts.passwd).register(manager)

    opts.logging and Logger().register(manager)

    if opts.profile and hotshot:
        profiler = hotshot.Profile(".profile")
        profiler.start()

    if opts.debug:
        print(graph(manager, name="circuits.web"))
        print()
        print(inspect(manager))

    for i in range(opts.jobs):
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
