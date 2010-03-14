#!/usr/bin/env python

from circuits import Component, Debugger
from circuits.net.sockets import TCPClient, Connect
from circuits.net.protocols.irc import IRC, PRIVMSG, USER, NICK, JOIN

class Bot(Component):

    def __init__(self, host, port=6667, channel=None):
        super(Bot, self).__init__(channel=channel)
        self += TCPClient(channel=channel) + IRC(channel=channel)
        self.push(Connect(host, port))

    def connected(self, host, port):
        self.push(USER("circuits", host, host, "Test circuits IRC Bot"))
        self.push(NICK("circuits"))
        self.push(JOIN("#shortcircuit"))
        self.push(JOIN("#softcircuit"))

    def numeric(self, source, target, numeric, args, message):
        if numeric == 433:
            self.push(NICK("%s_" % args))

    def message(self, source, target, message):
        self.push(PRIVMSG(source[0], message))

bot = Bot("irc.freenode.net", channel="bot") + Debugger()
bot.run()
