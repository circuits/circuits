#!/usr/bin/env python
"""Circuits IRC Client

A circuits based IRC Client demonstrating integration with urwid - a curses
application development library and interacting with and processing irc
events from an IRC server.

NB: This is not a full featured client.

For usage type:

   ./circ.py --help
"""
import os
import sys
from optparse import OptionParser
from re import compile as compile_regex
from select import select
from socket import gethostname

from urwid import AttrWrap, Edit, Frame, ListBox, Pile, SimpleListWalker, Text
from urwid.raw_display import Screen

from circuits import Component, __version__ as systemVersion, handler
from circuits.net.sockets import TCPClient, connect
from circuits.protocols.irc import (
    ERR_NICKNAMEINUSE, ERR_NOMOTD, IRC, JOIN, NICK, PART, PRIVMSG, QUIT,
    RPL_ENDOFMOTD, USER, Message, request,
)
from circuits.tools import getargspec

USAGE = "%prog [options] host [port]"
VERSION = "%prog v" + systemVersion

MAIN_TITLE = "cIRC - {0:s}".format(systemVersion)

HELP_STRINGS = {
    "main": "For help, type: /help"
}

CMD_REGEX = compile_regex(
    r"\/(?P<command>[a-z]+) ?"
    "(?P<args>.*)(?iu)"
)


def back_merge(l, n, t=" "):
    return l[:-n].extend([t.join(l[-n:])])


def parse_options():
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.add_option(
        "-c", "--channel",
        action="store", default="#circuits", dest="channel",
        help="Channel to join"
    )

    parser.add_option(
        "", "--debug",
        action="store_true", default=False, dest="debug",
        help="Enable debug mode"
    )

    parser.add_option(
        "-n", "--nick",
        action="store", default=os.environ["USER"], dest="nick",
        help="Nickname to use"
    )

    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit(1)

    return opts, args


class Client(Component):

    channel = "client"

    def init(self, host, port=6667, opts=None):
        self.host = host
        self.port = port
        self.opts = opts
        self.hostname = gethostname()

        self.nick = opts.nick
        self.ircchannel = opts.channel

        # Add TCPClient and IRC to the system.
        TCPClient(channel=self.channel).register(self)
        IRC(channel=self.channel).register(self)

        self.create_interface()

    def create_interface(self):
        self.screen = Screen()
        self.screen.start()

        self.screen.register_palette([
            ("title", "white", "dark blue", "standout"),
            ("line", "light gray", "black"),
            ("help", "white", "dark blue")]
        )

        self.body = ListBox(SimpleListWalker([]))
        self.lines = self.body.body

        self.title = Text(MAIN_TITLE)
        self.header = AttrWrap(self.title, "title")

        self.help = AttrWrap(
            Text(HELP_STRINGS["main"]),
            "help"
        )

        self.input = Edit(caption="%s> " % self.ircchannel)
        self.footer = Pile([self.help, self.input])

        self.top = Frame(self.body, self.header, self.footer)

    def ready(self, component):
        """Ready Event

        This event is triggered by the underlying ``TCPClient`` Component
        when it is ready to start making a new connection.
        """

        self.fire(connect(self.host, self.port))

    def connected(self, host, port):
        """connected Event

        This event is triggered by the underlying ``TCPClient`` Component
        when a successfully connection has been made.
        """

        nick = self.nick
        hostname = self.hostname
        name = "%s on %s using circuits/%s" % (nick, hostname, systemVersion)

        self.fire(NICK(nick))
        self.fire(USER(nick, hostname, host, name))

    def numeric(self, source, numeric, *args):
        """Numeric Event

        This event is triggered by the ``IRC`` Protocol Component when we have
        received an IRC Numberic Event from server we are connected to.
        """

        if numeric == ERR_NICKNAMEINUSE:
            self.fire(NICK("{0:s}_".format(args[0])))
        elif numeric in (RPL_ENDOFMOTD, ERR_NOMOTD):
            self.fire(JOIN(self.ircchannel))

    @handler("stopped", channel="*")
    def _on_stopped(self, component):
        self.screen.stop()

    @handler("generate_events")
    def _on_generate_events(self, event):
        event.reduce_time_left(0)

        size = self.screen.get_cols_rows()

        if not select(
                self.screen.get_input_descriptors(), [], [], 0.1)[0] == []:
            timeout, keys, raw = self.screen.get_input_nonblocking()

            for k in keys:
                if k == "window resize":
                    size = self.screen.get_cols_rows()
                    continue
                elif k == "enter":
                    self.processCommand(self.input.get_edit_text())
                    self.input.set_edit_text("")
                    continue

                self.top.keypress(size, k)
                self.input.set_edit_text(self.input.get_edit_text() + k)

        self.update_screen(size)

    def unknownCommand(self, command):
        self.lines.append(Text("Unknown command: %s" % command))

    def syntaxError(self, command, args, expected):
        self.lines.append(
            Text("Syntax error ({0:s}): {1:s} Expected: {2:s}".format(
                command, args, expected)
            )
        )

    def processCommand(self, s):  # noqa

        match = CMD_REGEX.match(s)
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
                                    f(*back_merge(tokens, factor))
                                else:
                                    self.syntaxError(
                                        command, " ".join(tokens),
                                        " ".join(
                                            x for x in args + [vargs]
                                            if x is not None
                                        )
                                    )
                            else:
                                f(*tokens)
                        elif default is not None and \
                                len(args) == (
                                    len(tokens) + len(default)):
                            f(*(tokens + list(default)))
                        else:
                            self.syntaxError(
                                command,
                                " ".join(tokens),
                                " ".join(
                                    x for x in args + [vargs]
                                    if x is not None
                                )
                            )
        else:
            if self.ircchannel is not None:
                self.lines.append(Text("<%s> %s" % (self.nick, s)))
                self.fire(PRIVMSG(self.ircchannel, s))
            else:
                self.lines.append(Text(
                    "No channel joined. Try /join #<channel>"))

    def cmdEXIT(self, message=""):
        self.fire(QUIT(message))
        raise SystemExit(0)

    def cmdSERVER(self, host, port=6667):
        self.fire(connect(host, port))

    def cmdSSLSERVER(self, host, port=6697):
        self.fire(connect(host, port, secure=True))

    def cmdJOIN(self, channel):
        if self.ircchannel is not None:
            self.cmdPART(self.ircchannel, "Joining %s" % channel)
        self.fire(JOIN(channel))
        self.ircchannel = channel

    def cmdPART(self, channel=None, message="Leaving"):
        if channel is None:
            channel = self.ircchannel
        if channel is not None:
            self.fire(PART(channel, message))
            self.ircchannel = None

    def cmdQUOTE(self, message):
        self.fire(request(Message(message)))

    def cmdQUIT(self, message="Bye"):
        self.fire(QUIT(message))

    def update_screen(self, size):
        canvas = self.top.render(size, focus=True)
        self.screen.draw_screen(size, canvas)

    @handler("notice", "privmsg")
    def _on_notice_or_privmsg(self, event, source, target, message):
        nick, ident, host = source

        if event.name == "notice":
            self.lines.append(Text("-%s- %s" % (nick, message)))
        else:
            self.lines.append(Text("<%s> %s" % (nick, message)))


def main():
    opts, args = parse_options()

    host = args[0]
    if len(args) > 1:
        port = int(args[1])
    else:
        port = 6667

    # Configure and run the system.

    client = Client(host, port, opts=opts)

    if opts.debug:
        from circuits import Debugger
        Debugger(file=sys.stderr).register(client)

    client.run()


if __name__ == "__main__":
    main()
