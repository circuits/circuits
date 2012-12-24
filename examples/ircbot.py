#!/usr/bin/env python

"""IRC Bot Example

This example shows how to use several components in circuits as well
as one of the builtin networking protocols. This IRC Bot simply connects
to the FreeNode IRC Network and joins the #circuits channel. It will also
echo anything privately messages to it in response.
"""


from circuits import Component, Debugger
from circuits.net.sockets import TCPClient, Connect
from circuits.net.protocols.irc import IRC, PRIVMSG, USER, NICK, JOIN

from circuits.net.protocols.irc import ERR_NICKNAMEINUSE
from circuits.net.protocols.irc import RPL_ENDOFMOTD, ERR_NOMOTD


class Bot(Component):

    # Define a separate channel so we can create many instances of ``Bot``
    channel = "ircbot"

    def init(self, host, port=6667, channel=channel):
        self.host = host
        self.port = port

        self += TCPClient(channel=self.channel) + IRC(channel=self.channel)

    def ready(self, component):
        """Ready Event

        This event is triggered by the underlying ``TCPClient`` Component
        when it is ready to start making a new connection.
        """

        self.fire(Connect(self.host, self.port))

    def connected(self, host, port):
        """Connected Event

        This event is triggered by the underlying ``TCPClient`` Component
        when a successfully connection has been made.
        """

        self.fire(USER("circuits", host, host, "Test circuits IRC Bot"))
        self.fire(NICK("circuits"))

    def numeric(self, source, target, numeric, args, message):
        """Numeric Event

        This event is triggered by the ``IRC`` Protocol Component when we have
        received an IRC Numberic Event from server we are connected to.
        """

        if numeric == ERR_NICKNAMEINUSE:
            self.fire(NICK("%s_" % args))
        if numeric in (RPL_ENDOFMOTD, ERR_NOMOTD):
            self.fire(JOIN("#circuits"))

    def message(self, source, target, message):
        """Message Event

        This event is triggered by the ``IRC`` Protocol Component for each
        message we receieve from the server.
        """

        self.fire(PRIVMSG(source[0], message))


# Configure and run the system
bot = Bot("irc.freenode.net") + Debugger()
bot.run()
