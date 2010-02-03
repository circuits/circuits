#!/usr/bin/env python

from circuits import Component, Debugger
from circuits.net.sockets import TCPClient, Connect
from circuits.net.protocols.irc import IRC, Message, User, Nick, Join

class Bot(Component):

    def __init__(self, host, port=6667, channel=None):
        super(Bot, self).__init__(channel=channel)
        self.client = TCPClient(channel=channel)
        self.irc = IRC(channel=channel)
        self.irc.register(self.client)
        self.client.register(self)
        self.push(Connect(host, port), "connect")

    def connected(self, host, port):
        self.push(User("circuits", host, host, "Test circuits IRC Bot"), "USER")
        self.push(Nick("circuits"), "NICK")
        self.push(Join("#circuits"), "JOIN")

    def numeric(self, source, target, numeric, args, message):
        if numeric == 433:
            self.push(Nick("%s_" % self.irc.getNick()), "NICK")

    def message(self, source, target, message):
        self.push(Message(source[0], message), "PRIVMSG")

bot = Bot("irc.freenode.net", channel="bot") + Debugger()
bot.run()
