#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) IRC Bot

A simple example of using circuits to build a simple IRC Bot.
This example demonstrates basic networking with circuits.
"""

from time import sleep
from socket import gethostname

from circuits import web
from circuits.lib.irc import IRC
from circuits.lib.sockets import TCPClient
from circuits import Manager, Component, Debugger

class Bot(Component):

    def __init__(self, *args, **kwargs):
        """Initialize Bot Component

        Create instances of the IRC and TCPClient Components and add them
        to our Bot Component.
        """

        # Important: Call the super constructors to initialize the Component.
        super(Bot, self).__init__(*args, **kwargs)

        self.irc = IRC(*args, **kwargs)
        self.client = TCPClient(*args, **kwargs)
        self += self.irc
        self += self.client

    def registered(self):
        self.manager += self.irc
        self.manager += self.client

    def connect(self, host, port=6667, ssl=False):
        "Connect to an IRC Server"

        self.client.open(host, port, ssl)

    def connected(self, host, port):
        """Connected Event Handler

        Event Handler for "connect" Events that implements:
         * When the Bot has connectd:
          * Send a USER command
          * Send a NICK command
        """

        self.irc.ircUSER("test", gethostname(), host, "Test Bot")
        self.irc.ircNICK("test")

    def numeric(self, source, target, numeric, args, message):
        """Numeric Event Handler

        Event Handler for "numeric" Events that implements:
         * When the Bot receives a numeric message:
          * If the numeric is a 433:
           * Change our nick by appending a "_" to our current nick

        Note: 433 is the IRC numeric for "Nickname in use"
        """

        if numeric == 433:
            self.irc.ircNICK("%s_" % self.irc.getNick())

    def message(self, source, target, message):
        """Message Event Handler

        Event Handler for "message" Events that implements:
         * When the Bot receives a message:
          * Echo the message back to the sender (source).
        """

        self.irc.ircPRIVMSG(source, message)

class Root(web.Controller):

    def index(self):
        return "Hello World!"

if __name__ == "__main__":
    manager = Manager() + Debugger()

    webserver = web.Server(8000, channel="web")
    manager += webserver + Root()

    bots = []
    for id in xrange(2):
        bot = Bot(channel=id)
        manager += bot
        bots.append(bot)
        bot.connect("irc.freenode.net")

    while True:
        try:
            manager.flush()
            [bot.client.poll() for bot in bots if bot.client.connected]
            webserver.poll()
        except KeyboardInterrupt:
            [bot.irc.ircQUIT() for bot in bots if bot.client.connected]
            manager.flush()
