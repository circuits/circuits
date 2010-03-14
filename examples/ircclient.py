#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) IRC Client

A basic IRC client with a very basic console interface.
"""

import os
import optparse
from socket import gethostname

from circuits.io import stdin
from circuits import handler, Component
from circuits import __version__ as systemVersion
from circuits.net.sockets import TCPClient, Connect
from circuits.net.protocols.irc import IRC, PRIVMSG, USER, NICK, JOIN

USAGE = "%prog [options] host [port]"
VERSION = "%prog v" + systemVersion

###
### Functions
###

def parse_options():
    """parse_options() -> opts, args

    Parse any command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-s", "--ssl",
            action="store_true", default=False, dest="ssl",
            help="Enable Secure Socket Layer (SSL)")

    parser.add_option("-n", "--nick",
            action="store", default=os.environ["USER"], dest="nick",
            help="Nickname to use")

    parser.add_option("-c", "--channel",
            action="store", default="#circuits", dest="channel",
            help="Channel to join")

    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit, 1

    return opts, args

###
### Components
###

class Client(Component):

    channel = "ircclient"

    def __init__(self, opts, host, port=6667):
        super(Client, self).__init__()

        self.opts = opts
        self.host = host
        self.port = port
        self.hostname = gethostname()

        self.nick = opts.nick
        self.ircchannel = opts.channel

        self += (TCPClient(channel=self.channel) + IRC(channel=self.channel))
        self.push(Connect(self.host, self.port), "connect")

    def connected(self, host, port):
        print "Connected to %s:%d" % (host, port)

        nick = self.nick
        hostname = self.hostname
        name = "%s on %s using circuits/%s" % (nick, hostname, systemVersion)

        self.push(USER(nick, hostname, host, name))
        self.push(NICK(nick))

    def disconnected(self):
        self.push(Connect(self.opts.host, self.opts.port), "connect")

    def numeric(self, source, target, numeric, args, message):
        if numeric == 1:
            self.push(JOIN(self.ircchannel))
        elif numeric == 433:
            self.nick = newnick = "%s_" % self.nick
            self.push(Nick(newnick), "NICK")

    def join(self, source, channel):
        if source[0].lower() == self.nick.lower():
            print "Joined %s" % channel
        else:
            print "--> %s (%s) has joined %s" % (source[0], source, channel)

    def notice(self, source, target, message):
        print "-%s- %s" % (source[0], message)

    def message(self, source, target, message):
        if target[0] == "#":
            print "<%s> %s" % (target, message)
        else:
            print "-%s- %s" % (source, message)

    @handler("read", target="stdin")
    def stdin_read(self, data):
        self.push(PRIVMSG(self.ircchannel, data.strip()))

###
### Main
###

def main():
    opts, args = parse_options()

    host = args[0]
    if len(args) > 1:
        port = int(args[1])
    else:
        port = 6667

    (Client(opts, host, port) + stdin).run()

###
### Entry Point
###

if __name__ == "__main__":
    main()
