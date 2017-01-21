#!/usr/bin/env python
"""Chat Server Example

This example demonstrates how to create a very simple telnet-style chat
server that supports many connecting clients.
"""
from optparse import OptionParser

from circuits import Component, Debugger
from circuits.net.events import write
from circuits.net.sockets import TCPServer

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


class ChatServer(Component):

    def init(self, args, opts):
        """Initialize our ``ChatServer`` Component.

        This uses the convenience ``init`` method which is called after the
        component is properly constructed and initialized and passed the
        same args and kwargs that were passed during construction.
        """

        self.args = args
        self.opts = opts

        self.clients = {}

        if opts.debug:
            Debugger().register(self)

        if ":" in opts.bind:
            address, port = opts.bind.split(":")
            port = int(port)
        else:
            address, port = opts.bind, 8000

        bind = (address, port)

        TCPServer(bind).register(self)

    def broadcast(self, data, exclude=None):
        exclude = exclude or []
        targets = (sock for sock in self.clients.keys() if sock not in exclude)
        for target in targets:
            self.fire(write(target, data))

    def connect(self, sock, host, port):
        """Connect Event -- Triggered for new connecting clients"""

        self.clients[sock] = {
            "host": sock,
            "port": port,
            "state": {
                "nickname": None,
                "registered": False
            }
        }

        self.fire(write(sock, b"Welcome to the circuits Chat Server!\n"))
        self.fire(write(sock, b"Please enter a desired nickname: "))

    def disconnect(self, sock):
        """Disconnect Event -- Triggered for disconnecting clients"""

        if sock not in self.clients:
            return

        nickname = self.clients[sock]["state"]["nickname"]

        self.broadcast(
            "!!! {0:s} has left !!!\n".format(nickname).encode("utf-8"),
            exclude=[sock]
        )

        del self.clients[sock]

    def read(self, sock, data):
        """Read Event -- Triggered for when client connections have data"""

        data = data.strip().decode("utf-8")

        if not self.clients[sock]["state"]["registered"]:
            nickname = data
            self.clients[sock]["state"]["registered"] = True
            self.clients[sock]["state"]["nickname"] = nickname

            self.broadcast(
                "!!! {0:s} has joined !!!\n".format(nickname).encode("utf-8"),
                exclude=[sock]
            )
        else:
            nickname = self.clients[sock]["state"]["nickname"]

            self.broadcast(
                "<{0:s}> {1:s}\n".format(nickname, data).encode("utf-8"),
                exclude=[sock]
            )


def main():
    opts, args = parse_options()

    # Configure and "run" the System.
    ChatServer(args, opts).run()


if __name__ == "__main__":
    main()
