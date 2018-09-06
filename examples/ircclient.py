#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Example IRC Client

A basic IRC client with a very basic console interface.

For usage type:

   ./ircclient.py --help

"""
from __future__ import print_function

import os
from optparse import OptionParser
from socket import gethostname

from circuits import Component, Debugger, __version__ as systemVersion, handler
from circuits.io import stdin
from circuits.net.events import connect
from circuits.net.sockets import TCPClient
from circuits.protocols.irc import IRC, JOIN, NICK, PRIVMSG, USER

USAGE = "%prog [options] host [port]"
VERSION = "%prog v" + systemVersion


def parse_options():
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.add_option(
        "-n", "--nick",
        action="store", default=os.environ["USER"], dest="nick",
        help="Nickname to use"
    )

    parser.add_option(
        "-d", "--debug",
        action="store_true", default=False, dest="debug",
        help="Enable debug verbose logging",
    )

    parser.add_option(
        "-c", "--channel",
        action="store", default="#circuits", dest="channel",
        help="Channel to join"
    )

    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit(1)

    return opts, args


class Client(Component):

    # Set a separate channel in case we want multiple ``Client`` instances.
    channel = "ircclient"

    def init(self, host, port=6667, opts=None):
        self.host = host
        self.port = port
        self.opts = opts
        self.hostname = gethostname()

        self.nick = opts.nick
        self.ircchannel = opts.channel

        # Add TCPClient and IRC to the system.
        TCPClient(channel=self.channel).register(self)
        IRC(channel=self.channel).register(self)

        # Enable Debugging?
        if opts.debug:
            Debugger().register(self)

    def ready(self, component):
        """ready Event

        This event is triggered by the underlying ``TCPClient`` Component
        when it is ready to start making a new connection.
        """

        self.fire(connect(self.host, self.port))

    def connected(self, host, port):
        """connected Event

        This event is triggered by the underlying ``TCPClient`` Component
        when a successfully connection has been made.
        """

        print("Connected to %s:%d" % (host, port))

        nick = self.nick
        hostname = self.hostname
        name = "%s on %s using circuits/%s" % (nick, hostname, systemVersion)

        self.fire(NICK(nick))
        self.fire(USER(nick, nick, self.hostname, name))

    def disconnected(self):
        """disconnected Event

        This event is triggered by the underlying ``TCPClient`` Component
        when the connection has been disconnected.
        """

        print("Disconnecetd from %s:%d" % (self.host, self.port))

        raise SystemExit(0)

    def numeric(self, source, numeric, *args):
        """numeric Event

        This event is triggered by the ``IRC`` Protocol Component when we have
        received an IRC Numberic Event from server we are connected to.
        """

        if numeric == 1:
            self.fire(JOIN(self.ircchannel))
        elif numeric == 433:
            self.nick = newnick = "%s_" % self.nick
            self.fire(NICK(newnick))

    def join(self, source, channel):
        """join Event

        This event is triggered by the ``IRC`` Protocol Component when a
        user has joined a channel.
        """

        if source[0].lower() == self.nick.lower():
            print("Joined %s" % channel)
        else:
            print(
                "--> %s (%s) has joined %s" % (
                    source[0], "@".join(source[1:]), channel
                )
            )

    def notice(self, source, target, message):
        """notice Event

        This event is triggered by the ``IRC`` Protocol Component for each
        notice we receieve from the server.
        """

        print("-%s- %s" % (source[0], message))

    def privmsg(self, source, target, message):
        """privmsg Event

        This event is triggered by the ``IRC`` Protocol Component for each
        message we receieve from the server.
        """

        if target[0] == "#":
            print("<%s> %s" % (source[0], message))
        else:
            print("-%s- %s" % (source[0], message))

    @handler("read", channel="stdin")
    def stdin_read(self, data):
        """read Event (on channel ``stdin``)

        This is the event handler for ``read`` events specifically from the
        ``stdin`` channel. This is triggered each time stdin has data that
        it has read.
        """

        data = data.strip().decode("utf-8")

        print("<{0:s}> {1:s}".format(self.nick, data))
        self.fire(PRIVMSG(self.ircchannel, data))


def main():
    opts, args = parse_options()

    host = args[0]
    if len(args) > 1:
        port = int(args[1])
    else:
        port = 6667

    # Configure and run the system.
    client = Client(host, port, opts=opts)
    stdin.register(client)
    client.run()


if __name__ == "__main__":
    main()
