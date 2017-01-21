#!/usr/bin/env python
"""IRC Bot Example

This example shows how to use several components in circuits as well
as one of the builtin networking protocols. This IRC Bot simply connects
to the FreeNode IRC Network and joins the #circuits channel. It will also
echo anything privately messages to it in response.
"""
import sys

from circuits import Component, Debugger
from circuits.net.sockets import TCPClient, connect
from circuits.protocols.irc import (
    ERR_NICKNAMEINUSE, ERR_NOMOTD, IRC, JOIN, NICK, PRIVMSG, RPL_ENDOFMOTD,
    USER,
)


class Bot(Component):

    # Define a separate channel so we can create many instances of ``Bot``
    channel = "ircbot"

    def init(self, host="irc.freenode.net", port="6667", channel=channel):
        self.host = host
        self.port = int(port)

        # Add TCPClient and IRC to the system.
        TCPClient(channel=self.channel).register(self)
        IRC(channel=self.channel).register(self)

    def ready(self, component):
        """Ready Event

        This event is triggered by the underlying ``TCPClient`` Component
        when it is ready to start making a new connection.
        """

        self.fire(connect(self.host, self.port))

    def connected(self, host, port):
        """connected Event

        This event is triggered by the underlying ``TCPClient`` Component
        when a successfully connection has been made.
        """

        self.fire(NICK("circuits"))
        self.fire(USER("circuits", "circuits", host, "Test circuits IRC Bot"))

    def disconnected(self):
        """disconnected Event

        This event is triggered by the underlying ``TCPClient`` Component
        when the connection is lost.
        """

        raise SystemExit(0)

    def numeric(self, source, numeric, *args):
        """Numeric Event

        This event is triggered by the ``IRC`` Protocol Component when we have
        received an IRC Numberic Event from server we are connected to.
        """

        if numeric == ERR_NICKNAMEINUSE:
            self.fire(NICK("{0:s}_".format(args[0])))
        elif numeric in (RPL_ENDOFMOTD, ERR_NOMOTD):
            self.fire(JOIN("#circuits"))

    def privmsg(self, source, target, message):
        """Message Event

        This event is triggered by the ``IRC`` Protocol Component for each
        message we receieve from the server.
        """

        if target.startswith("#"):
            self.fire(PRIVMSG(target, message))
        else:
            self.fire(PRIVMSG(source[0], message))


# Configure and run the system
bot = Bot(*sys.argv[1:])

Debugger().register(bot)

# To register a 2nd ``Bot`` instance. Simply use a separate channel.
# Bot(*sys.argv[1:], channel="foo").register(bot)

bot.run()
