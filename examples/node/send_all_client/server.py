#!/usr/bin/env python
from datetime import datetime
from optparse import OptionParser

from circuits import Component, Debugger, Event, Timer
from circuits.node import Node

__version__ = "0.0.1"

USAGE = "%prog [options]"
VERSION = "%prog v" + __version__


def parse_options():
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.add_option(
        "-b", "--bind",
        action="store", type="string",
        default="0.0.0.0:8000", dest="bind",
        help="Bind to address:[port]"
    )

    parser.add_option(
        "-d", "--debug",
        action="store_true",
        default=False, dest="debug",
        help="Enable debug mode"
    )

    opts, args = parser.parse_args()

    return opts, args


class send_all_event(Event):

    def __init__(self, infos):
        super(send_all_event, self).__init__(infos)


class NodeServer(Component):

    def init(self, args, opts):
        if opts.debug:
            Debugger().register(self)

        if ":" in opts.bind:
            address, port = opts.bind.split(":")
            port = int(port)
        else:
            address, port = opts.bind, 8000

        self.node = Node(port=port, server_ip=address).register(self)

    def connect(self, sock, host, port):
        print('Peer connected: %s:%d' % (host, port))

    def disconnect(self, sock):
        print('Peer disconnected: %s' % sock)

    def ready(self, server, bind):
        print('Server ready: %s:%d' % bind)
        Timer(3, Event.create('send_all'), persist=True).register(self)

    def send_all(self):
        event = send_all_event(str(datetime.now()))
        print('send: %s' % event)
        self.node.server.send_all(event)


def main():
    opts, args = parse_options()

    # Configure and "run" the System.
    NodeServer(args, opts).run()


if __name__ == "__main__":
    main()
