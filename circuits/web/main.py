#!/usr/bin/env python
"""
Main

circutis.web Web Server and Testing Tool.
"""

import os
from argparse import ArgumentParser
from hashlib import md5
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


def parse_options():
    parser = ArgumentParser()

    parser.add_argument(
        '-b',
        '--bind',
        action='store',
        default='0.0.0.0:8000',
        help='Bind to address:[port]',
    )

    parser.add_argument(
        '-l',
        '--logging',
        action='store_true',
        default=False,
        help='Enable logging of requests',
    )

    parser.add_argument(
        '-p',
        '--passwd',
        action='store',
        default=None,
        help='Location to passwd file for Digest Auth',
    )

    parser.add_argument(
        '-j',
        '--jobs',
        action='store',
        type=int,
        default=0,
        help='Specify number of jobs/processes to start',
    )

    parser.add_argument(
        '--poller',
        action='store',
        default='select',
        help='Specify type of poller to use',
    )

    parser.add_argument(
        '--server',
        action='store',
        default='server',
        help='Specify server to use',
    )

    parser.add_argument(
        '--profile',
        action='store_true',
        default=False,
        help='Enable execution profiling support',
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help='Enable debug mode',
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        default=False,
        help='Enable WSGI validation mode',
    )

    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s v{circuits.__version__}')

    parser.add_argument('docroot', nargs='?', default=os.getcwd())

    return parser.parse_args()


class Authentication(Component):
    channel = 'web'

    realm = 'Secure Area'
    users = {'admin': md5(b'admin').hexdigest()}

    def __init__(self, channel=channel, realm=None, passwd=None):
        super().__init__(self, channel=channel)

        if realm is not None:
            self.realm = realm

        if passwd is not None:
            with open(passwd) as f:
                lines = (line.strip() for line in f)
                self.users = dict(line.split(':', 1) for line in lines)

    @handler('request', priority=10)
    def request(self, event, request, response):
        if not check_auth(request, response, self.realm, self.users):
            event.stop()
            return digest_auth(request, response, self.realm, self.users)
        return None


class HelloWorld(Component):
    channel = 'web'

    def request(self, request, response):
        return 'Hello World!'


class Root(Controller):
    def hello(self):
        return 'Hello World!'


def select_poller(poller):
    if poller == 'poll':
        if Poll is None:
            stderr.write(
                'No poll support available - defaulting to Select...',
            )
            Poller = Select
        else:
            Poller = Poll
    elif poller == 'epoll':
        if EPoll is None:
            stderr.write(
                'No epoll support available - defaulting to Select...',
            )
            Poller = Select
        else:
            Poller = EPoll
    else:
        Poller = Select

    return Poller


def parse_bind(bind):
    if ':' in bind:
        address, port = bind.split(':')
        port = int(port)
    else:
        address, port = bind, 8000

    return (address, port)


def main():
    opts = parse_options()

    bind = parse_bind(opts.bind)

    if opts.validate:
        application = Application() + Root()
        app = validator(application)

        httpd = make_server(bind[0], bind[1], app)
        httpd.serve_forever()

        raise SystemExit(0)

    manager = Manager()

    opts.debug and Debugger().register(manager)

    Poller = select_poller(opts.poller.lower())
    Poller().register(manager)

    if opts.server.lower() == 'base':
        BaseServer(bind).register(manager)
        HelloWorld().register(manager)
    else:
        Server(bind).register(manager)
        Root().register(manager)

    Static(docroot=opts.docroot, dirlisting=True).register(manager)

    opts.passwd and Authentication(passwd=opts.passwd).register(manager)

    opts.logging and Logger().register(manager)

    if opts.profile and hotshot:
        profiler = hotshot.Profile('.profile')
        profiler.start()

    if opts.debug:
        print(graph(manager, name='circuits.web'))
        print()
        print(inspect(manager))

    for _i in range(opts.jobs):
        manager.start(process=True)

    manager.run()

    if opts.profile and hotshot:
        profiler.stop()
        profiler.close()

        stats = hotshot.stats.load('.profile')
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(20)


if __name__ == '__main__':
    main()
