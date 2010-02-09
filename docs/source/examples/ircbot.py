#!/usr/bin/env python

from circuits import Component
from circuits.net.sockets import TCPClient, Connect
from circuits.net.protocols.irc import IRC, Message, User, Nick

class Bot(Component):

    def __init__(self, host, port=6667, channel=None):
        super(Bot, self).__init__(channel=channel)

        self += TCPClient(channel=channel) + IRC(channel=channel)
        self.push(Connect(host, port))

    def connected(self, host, port):
        self.push(User("test", host, host, "Test Bot"), "USER")
        self.push(Nick("test"), "NICK")

    def numeric(self, source, target, numeric, args, message):
        if numeric == 433:
            self.push(Nick("%s_" % args), "NICK")

    def message(self, source, target, message):
        self.push(Message(source[0], message), "PRIVMSG")

Bot("irc.freenode.net", channel="bot").run()
