#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""MTA/MDA

Simple SMTP Server / Mail Transfer Agent (MTA) and Mail Delivery Agent (MDA).
Mail is delivered into Maildir mailboxes. No filterting or forwarding support
is available. The MTA only implements the minimum required set of SMTP
commands.
"""

import os
import sys
import optparse
from mailbox import Maildir

from circuits import __version__
from circuits.app import Daemon
from circuits.net.sockets import TCPServer
from circuits.net.protocols.smtp import SMTP
from circuits import handler, Event, Component, Manager, Debugger

USAGE = "%prog [options]"
VERSION = "%prog v" + __version__

###
### Functions
###

def parse_options():
    """parse_options() -> opts, args

    Parse any command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("", "--debug",
            action="store_true", default=False, dest="debug",
            help="Enable debugging mode")

    parser.add_option("-d", "--daemon",
            action="store_true", default=False, dest="daemon",
            help="Enable daemon mode (Default: False)")

    parser.add_option("-b", "--bind",
            action="store", type="str", default="0.0.0.0:25", dest="bind",
            help="Bind to address:[port]")

    parser.add_option("-p", "--path",
            action="store", default="/var/mail/", dest="path",
            help="Path to store mailI (Default: /var/mail/)")

    opts, args = parser.parse_args()

    return opts, args

###
### Components
###

class MDA(Component):

    def __init__(self, *args, **kwargs):
        super(MDA, self).__init__(*args, **kwargs)

        self.__path = kwargs.get("path", "/var/mail/")

    def message(self, sock, mailfrom, rcpttos, data):
        for recipient in rcpttos:
            self.deliver(data, recipient)
        data.close()

    def deliver(self, message, recipient):
        user, domains = recipient.split("@")
        mailbox = Maildir(os.path.join(self.__path, user), factory=None)
        mailbox.add(message)
        mailbox.flush()
        mailbox.close()

class MTA(TCPServer, SMTP):

    def helo(self, sock, hostname):
        print >> sys.stderr, "%s Got HELO, hostname: %s" % (sock, hostname)

    def mail(self, sock, sender):
        print >> sys.stderr, "%s Got MAIL, sender: %s" % (sock, sender)

    def rcpt(self, sock, recipient):
        print >> sys.stderr, "%s Got RCPT, recipient: %s" % (sock, recipient)

    def noop(self, sock):
        print >> sys.stderr, "%s Got NOOP" % sock

    def rset(self, sock):
        print >> sys.stderr, "%s Got RSET" % sock

    def data(self, sock):
        print >> sys.stderr, "%s Got DATA" % sock

    def quit(self, sock):
        print >> sys.stderr, "%s Got QUIT" % sock

    def disconnect(self, sock):
        print >> sys.stderr, "%s Disconnected" % sock

    def error(self, sock, error):
        print >> sys.stderr, "%s Error: %s" % (sock, error)

    def message(self, sock, mailfrom, rcpttos, data):
        print >> sys.stderr, "New Mail Message\n"
        print >> sys.stderr, "From: %s" % mailfrom
        print >> sys.stderr, "To: %s\n" % ",".join(rcpttos)

        for line in data:
            print >> sys.stderr, line

###
### Main
###

def main():
    opts, args = parse_options()

    if ":" in opts.bind:
        address, port = opts.bind.split(":")
        port = int(port)
    else:
        address, port = opts.bind, 25

    path = opts.path
    daemon = opts.daemon

    if not os.path.exists(path):
        os.makedirs(path)

    m = Manager()

    if opts.debug:
        m += Debugger()

    m += MTA((address, port))
    m += MDA(path=opts.path)

    if opts.daemon:
        m += Daemon()

    m.run()

###
### Entry Point
###

if __name__ == "__main__":
    main()
