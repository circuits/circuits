#!/usr/bin/env python
from optparse import OptionParser

from circuits import Component, Debugger
from circuits.node import Node

__version__ = "0.0.1"

USAGE = "%prog [options]"
VERSION = "%prog v" + __version__


def parse_options():
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.add_option(
        "-i", "--ip",
        action="store", type="string",
        default="127.0.0.1:8000", dest="bind",
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


class NodeClient(Component):

    def init(self, args, opts):
        if opts.debug:
            Debugger().register(self)

        if ":" in opts.bind:
            address, port = opts.bind.split(":")
            port = int(port)
        else:
            address, port = opts.bind, 8000

        node = Node().register(self)
        node.add('peer_name', address, port)

    def send_all_event(self, infos):
        print('receive: %s' % infos)


def main():
    opts, args = parse_options()

    # Configure and "run" the System.
    NodeClient(args, opts).run()


if __name__ == "__main__":
    main()
