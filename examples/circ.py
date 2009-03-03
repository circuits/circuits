#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""Circuits IRC Client

A circuits based IRC Client demonstrating integration with urwid - a curses
application development library and interacting with and processing irc
events from an IRC server.

NB: This is not a full featured client.
"""

import re
import os
import urwid
from select import select
from socket import gethostname
from inspect import getargspec
from traceback import format_exc
from urwid.raw_display import Screen

from circuits import __version__
from circuits.lib.sockets import TCPClient
from circuits import listener, Event, Component, Manager
from circuits.lib.irc import sourceSplit, IRC, ERR_NICKNAMEINUSE

MAIN_TITLE = "cIRC - %s" % __version__

HELP_STRINGS = {
    "main": "For help, type: /help"
}

def backMerge(l, n, t=" "):
    return l[:-n] + [t.join(l[-n:])]

class IrcClient(Component):

    channel = "irc"

    def __init__(self, *args, **kwargs):
        super(IrcClient, self).__init__(*args, **kwargs)

        self.irc = IRC()
        self.tcpClient = TCPClient()

    def registered(self, component, manager):
        manager += self.irc
        manager += self.tcpClient

    def poll(self):
        self.tcpClient.poll()

    @listener("connect")
    def onCONNECT(self, host, port):
        self.irc.ircUSER("circ", gethostname(), host, "circuits IRC Client")
        self.irc.ircNICK(self.irc.getNick())

    @listener("numeric")
    def onNUMERIC(self, source, target, numeric, arg, message):
        if numeric == ERR_NICKNAMEINUSE:
            self.irc.ircNICK(self.irc.getNick() + "_")
        else:
            if arg is not None:
                self.lines.append(urwid.Text("%s :%s" % (arg, message)))
            else:
                self.lines.append(urwid.Text(message))

    @listener("notice")
    def onNOTICE(self, source, target, message):
        if type(source) == str:
            nick = source
        else:
            nick, ident, host = sourceSplit(source)

        self.push(Event(nick, message), "notice", "ui")

    @listener("message")
    def onMESSAGE(self, source, target, message):
        if type(source) == str:
            nick = source
        else:
            nick, ident, host = sourceSplit(source)

        self.push(Event(nick, message), "message", "ui")

    
class MainWindow(Screen, Component):

    channel = "ui"

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.nick = os.environ.get("USER", "circ")
        self.channel = None

        self.cmdRegex = re.compile(
                "\/(?P<command>[a-z]+) ?"
                "(?P<args>.*)(?iu)")

        self.register_palette([
                ("title", "white", "dark blue", "standout"),
                ("line", "light gray", "black"),
                ("help", "white", "dark blue")])

        self.body = urwid.ListBox([])
        self.lines = self.body.body

        self.title = urwid.Text(MAIN_TITLE)
        self.header = urwid.AttrWrap(self.title, "title")

        self.help = urwid.AttrWrap(
                urwid.Text(
                    HELP_STRINGS["main"]), "help")
        self.input = urwid.Edit(caption="%s> " % self.channel)
        self.footer = urwid.Pile([self.help, self.input])

        self.top = urwid.Frame(self.body, self.header,
                self.footer)

    def poll(self):
        size = self.get_cols_rows()

        if not select(self.get_input_descriptors(), [], [], 0.1)[0] == []:
            timeout, keys, raw = self.get_input_nonblocking()

            for k in keys:
                if k == "window resize":
                    size = self.get_cols_rows()
                    continue
                elif k == "enter":
                    self.processCommand(self.input.get_edit_text())
                    self.input.set_edit_text("")
                    continue

                self.top.keypress(size, k)
                self.input.set_edit_text(self.input.get_edit_text() + k)

        self.update_screen(size)

    def unknownCommand(self, command):
        self.lines.append(urwid.Text("Unknown command: %s" % command))

    def syntaxError(self, command, args, expected):
        self.lines.append(
                urwid.Text(
                    "Syntax error (%s): %s Expected: %s" % (
                        command, args, expected)))

    def processCommand(self, s):

        match = self.cmdRegex.match(s)
        if match is not None:

            command = match.groupdict()["command"]
            if not match.groupdict()["args"] == "":
                tokens = match.groupdict()["args"].split(" ")
            else:
                tokens = []

            fn = "cmd" + command.upper()
            if hasattr(self, fn):
                f = getattr(self, fn)
                if callable(f):

                    args, vargs, kwargs, default = getargspec(f)
                    args.remove("self")
                    if len(args) == len(tokens):
                        if len(args) == 0:
                            f()
                        else:
                            f(*tokens)
                    else:
                        if len(tokens) > len(args):
                            if vargs is None:
                                if len(args) > 0:
                                    factor = len(tokens) - len(args) + 1
                                    f(*backMerge(tokens, factor))
                                else:
                                    print "1"
                                    self.syntaxError(command,
                                            " ".join(tokens),
                                            " ".join(
                                                [x for x in args + [vargs]
                                                    if x is not None]))
                            else:
                                f(*tokens)
                        elif default is not None and \
                                len(args) == (
                                        len(tokens) + len(default)):
                            f(*(tokens + list(default)))
                        else:
                            self.syntaxError(command,
                                    " ".join(tokens),
                                    " ".join(
                                        [x for x in args + [vargs]
                                            if x is not None]))
        else:
            if self.channel is not None:
                self.lines.append(urwid.Text("<%s> %s" % (self.nick, s)))
                self.push(Event(self.channel, s), "privmsg", "irc")
            else:
                self.lines.append(urwid.Text(
                    "No channel joined. Try /join #<channel>"))

    def cmdEXIT(self, message=""):
        self.push(Event(message), "quit", "irc")
        raise SystemExit, 0

    def cmdSERVER(self, host, port=6667):
        self.push(Event(host, int(port)), "connect", "irc")

    def cmdSSLSERVER(self, host, port=6697):
        self.push(Event(host, int(port), ssl=True), "connect", "irc")

    def cmdJOIN(self, channel):
        if self.channel is not None:
            self.cmdPART(self.channel, "Joining %s" % channel)
        self.push(Event(channel), "join", "irc")
        self.channel = channel

    def cmdPART(self, channel=None, message="Leaving"):
        if channel is None:
            channel = self.channel
        if channel is not None:
            self.push(Event(channel, message), "part", "irc")
            self.channel = None

    def cmdQUOTE(self, message):
        self.push(Event(message), "raw", "irc")

    def cmdQUIT(self, message="Bye"):
        self.push(Event(message), "quit", "irc")

    def update_screen(self, size):
        canvas = self.top.render(size, focus=True)
        self.draw_screen(size, canvas)

    @listener("notice", "message")
    def onMESSAGE(self, event, nick, message):
        if event.channel == "notice":
            self.lines.append(urwid.Text("-%s- %s" % (nick, message)))
        else:
            self.lines.append(urwid.Text("<%s> %s" % (nick, message)))

def main():
    manager = Manager()
    ircClient = IrcClient()
    mainWindow = MainWindow()

    manager += ircClient
    manager += mainWindow

    mainWindow.start()

    while True:
        try:
            ircClient.poll()
            mainWindow.poll()
            manager.flush()
        except KeyboardInterrupt:
            mainWindow.stop()
            break
        except SystemExit:
            mainWindow.stop()
            break
        except Exception, error:
            mainWindow.stop()
            print "ERROR: %s" % error
            print format_exc()
            break

if __name__ == "__main__":
    main()
