#!/usr/bin/env python

import optparse
from uuid import uuid4 as uuid

from circuits.app import Daemon
from circuits import handler, Component, Debugger
from circuits.net.sockets import TCPClient, TCPServer
from circuits.net.sockets import UDPClient, UDPServer
from circuits.net.sockets import Close, Connect, Write

__version__ = "0.2"

USAGE = "%prog [options] <source> <target>"
VERSION = "%prog v" + __version__

EPILOG = """
Creates a listening socket on the given <source> and directs all traffic
to the given <target>. Specify the protocol with the -p/--procotol
option (default: tcp).

The format of <source> and <target> are as follows:

    <source>     -> <address>:<port>
    <target -> <address>[:<port>]

Where:
    <address> Is an IPv4 address of the form a.b.c.d (eg: 127.0.0.1)
              Use 0.0.0.0 to listen to all interfaces.
    <port>    Is a valid port (integer) to listen for incoming connections.
"""


def parse_options():
    parser = optparse.OptionParser(usage=USAGE, version=VERSION,
            epilog=EPILOG)

    parser.add_option("-d", "--daemon",
            action="store_true", default=False, dest="daemon",
            help="Enable daemon mode (fork into the background)")

    parser.add_option("", "--debug",
            action="store_true", default=False, dest="debug",
            help="Enable debug mode (verbose event output)")

    parser.add_option("-s", "--ssl",
            action="store_true", default=False, dest="ssl",
            help="Enable SSL (Secure Socket Layer)")

    parser.add_option("-p", "--protocol",
            action="store", default="tcp", dest="protocol",
            help="Specify IP Protocol (tcp od udp)")

    opts, args = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        raise SystemExit(1)

    return opts, args


def _on_target_disconnected(self, event):
    channel = event.channels[0]
    sock = self._sockets[channel]

    if self._protocol == "tcp":
        self.fire(Close(sock), "source")

    del self._sockets[channel]
    del self._clients[sock]


def _on_target_ready(self, component):
    self.fire(Connect(*self._target, secure=self._secure), component.channel)


def _on_target_read(self, event, data):
    sock = self._sockets[event.channels[0]]
    self.fire(Write(sock, data), "source")


class PortForwarder(Component):

    def __init__(self, source, target, secure=False, protocol="tcp"):
        super(PortForwarder, self).__init__()

        self._source = source
        self._target = target
        self._secure = secure
        self._protocol = protocol

        self._clients = dict()
        self._sockets = dict()

        Server = TCPServer if self._protocol == "tcp" else UDPServer
        server = Server(self._source, secure=self._secure, channel="source")
        server.register(self)

    @handler("connect", channel="source")
    def _on_source_connect(self, sock, host, port):
        bind = 0
        channel = uuid()

        client = TCPClient(bind, channel=channel)
        client.register(self)

        self.addHandler(
                handler("disconnected", channel=channel)
                (_on_target_disconnected))

        self.addHandler(
                handler("ready", channel=channel)
                (_on_target_ready))

        self.addHandler(
                handler("read", channel=channel)
                (_on_target_read))

        self._clients[sock] = client
        self._sockets[client.channel] = sock

    @handler("read", channel="source")
    def _on_source_read(self, sock, data):
        if self._protocol == "tcp":
            client = self._clients[sock]
            self.fire(Write(data), client.channel)
        else:
            host, port = sock
            self.fire(Write(sock, data), "source")


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

    if type(target) is not tuple:
        target = target, source[1]

    system = PortForwarder(source, target, protocol=opts.protocol)

    if opts.daemon:
        Daemon("portforward.pid").register(system)

    if opts.debug:
        Debugger().register(system)

    system.run()

if __name__ == "__main__":
    main()
