#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) IRC Client

A basic IRC client with a very basic console interface.
"""

import optparse

from circuits.lib.io import stdin
from circuits import handler, Component, Manager
from circuits import __version__ as systemVersion
from circuits.lib.irc import IRC, Message, User, Nick
from circuits.lib.sockets import TCPClient, Connect, Write

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
        super(Bot, self).__init__()

        self.opts = opts
        self.host = host
        self.port = port
        self.hostname = gethostname()
        self.ircchannel = opts.channel

        self += (TCPClient(channel=self.channel) + IRC(channel=self.channel))
        self.push(Connect(self.host, self.port), "connect")

    def connected(self, host, port):
        nick = self.opts.nick
        hostname = self.hostname
        name = "%s on %s using circuits/%s" % (nick, hostname, systemVersion)
        ircchannel = self.ircchannel

        self.push(User(self.opts.nick, hostname, host, name), "USER")
        self.push(Nick(nick), "NICK")
        self.push(Join(channel), "JOIN")

    def disconnected(self):
        self.push(Connect(self.opts.host, self.opts.port), "connect")

    def numeric(self, source, target, numeric, args, message):
        if numeric == 433:
            self.nick = newnick = "%s_" % self.nick
            self.push(Nick(newnick), "NICK")

    def message(self, source, target, message):
        if target[0] == "#":
            print "<%s> %s" % (target, message)
        else:
            print "-%s- %s" % (source, message)

    @handler("read", target="stdin")
    def stdin_read(self, data):
        self.push(Message(self.ircchannel, data.strip()), "PRIVMSG")

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

    (Telnet(opts, host, port) + stdin).run()

###
### Entry Point
###

if __name__ == "__main__":
    main()
