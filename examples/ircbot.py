#!/usr/bin/env python

from circuits import Component, Debugger
from circuits.net.sockets import TCPClient, Connect
from circuits.net.protocols.irc import IRC, PRIVMSG, USER, NICK, JOIN

from circuits.net.protocols.irc import ERR_NICKNAMEINUSE
from circuits.net.protocols.irc import RPL_ENDOFMOTD, ERR_NOMOTD

class Bot(Component):

    channel = "ircbot"

    def __init__(self, host, port=6667, channel=channel):
        super(Bot, self).__init__()

        self._host = host
        self._port = port

        self += TCPClient(channel=self.channel) + IRC(channel=self.channel)

    def ready(self, component):
        self.push(Connect(self._host, self._port))

    def connected(self, host, port):
        self.push(USER("circuits", host, host, "Test circuits IRC Bot"))
        self.push(NICK("circuits"))

    def numeric(self, source, target, numeric, args, message):
        if numeric == ERR_NICKNAMEINUSE:
            self.push(NICK("%s_" % args))
        if numeric in (RPL_ENDOFMOTD, ERR_NOMOTD):
            self.push(JOIN("#circuits"))

    def message(self, source, target, message):
        self.push(PRIVMSG(source[0], message))

bot = Bot("irc.freenode.net") + Debugger()
bot.run()
