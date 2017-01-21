#!/usr/bin/env python
"""A Port Forwarding Example

This example demonstrates slightly more complex features and behaviors
implementing a TCP/UDP Port Forwarder of network traffic. This can be used
as a simple tool to forward traffic from one port to another.

Example:

    ./portforward.py 0.0.0.0:2222 127.0.0.1:22

This example also has support for daemonizing the process into the background.
"""
from optparse import OptionParser
from uuid import uuid4 as uuid

from circuits import Component, Debugger, handler
from circuits.app import Daemon
from circuits.net.events import close, connect, write
from circuits.net.sockets import TCPClient, TCPServer

__version__ = "0.2"

USAGE = "%prog [options] <srcaddr:srcport> <destaddr:destport>"
VERSION = "%prog v" + __version__


def parse_options():
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.add_option(
        "-d", "--daemon",
        action="store_true", default=False, dest="daemon",
        help="Enable daemon mode (fork into the background)"
    )

    parser.add_option(
        "", "--debug",
        action="store_true", default=False, dest="debug",
        help="Enable debug mode (verbose event output)"
    )

    opts, args = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        raise SystemExit(1)

    return opts, args


def _on_target_disconnected(self, event):
    """Disconnected Event Handler

    This unbound function will be later added as an event handler to a
    dynamically created and registered client instance and used to process
    Disconnected events of a connected client.
    """

    channel = event.channels[0]
    sock = self._sockets[channel]

    self.fire(close(sock), "source")

    del self._sockets[channel]
    del self._clients[sock]


def _on_target_ready(self, component):
    """Ready Event Handler

    This unbound function will be later added as an event handler to a
    dynamically created and registered client instance and used to process
    Ready events of a registered client.
    """

    self.fire(connect(*self._target, secure=self._secure), component.channel)


def _on_target_read(self, event, data):
    """Read Event Handler

    This unbound function will be later added as an event handler to a
    dynamically created and registered client instance and used to process
    Read events of a connected client.
    """

    sock = self._sockets[event.channels[0]]
    self.fire(write(sock, data), "source")


class PortForwarder(Component):

    def init(self, source, target, secure=False):
        self._source = source
        self._target = target
        self._secure = secure

        self._clients = dict()
        self._sockets = dict()

        # Setup our components and register them.
        server = TCPServer(self._source, secure=self._secure, channel="source")
        server.register(self)

    @handler("connect", channel="source")
    def _on_source_connect(self, sock, host, port):
        """Explicitly defined connect Event Handler

        This evens is triggered by the underlying TCPServer Component when
        a new client connection has been made.

        Here we dynamically create a Client instance, registere it and add
        custom event handlers to handle the events of the newly created
        client. The client is registered with a unique channel per connection.
        """

        bind = 0
        channel = uuid()

        client = TCPClient(bind, channel=channel)
        client.register(self)

        self.addHandler(
            handler("disconnected", channel=channel)(_on_target_disconnected)
        )

        self.addHandler(
            handler("ready", channel=channel)(_on_target_ready)
        )

        self.addHandler(
            handler("read", channel=channel)(_on_target_read)
        )

        self._clients[sock] = client
        self._sockets[client.channel] = sock

    @handler("read", channel="source")
    def _on_source_read(self, sock, data):
        """Explicitly defined Read Event Handler

        This evens is triggered by the underlying TCPServer Component when
        a connected client has some data ready to be processed.

        Here we simply fire a cooresponding write event to the cooresponding
        matching client which we lookup using the socket object as the key
        to determinte the unique id.
        """

        client = self._clients[sock]
        self.fire(write(data), client.channel)


def sanitize(s):
    if ":" in s:
        address, port = s.split(":")
        port = int(port)
        return address, port
    return s


def main():
    opts, args = parse_options()

    source = sanitize(args[0])
    target = sanitize(args[1])

    if type(source) is not tuple:
        print("ERROR: source address must specify port (address:port)")
        raise SystemExit(-1)

    if type(target) is not tuple:
        print("ERROR: target address must specify port (address:port)")
        raise SystemExit(-1)

    system = PortForwarder(source, target)

    if opts.daemon:
        Daemon("portforward.pid").register(system)

    if opts.debug:
        Debugger().register(system)

    system.run()


if __name__ == "__main__":
    main()
