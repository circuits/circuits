# Module:   protocol
# Date:     11th August 2014
# Author:   James Mills <prologic@shortcircuit.net.au>


"""Internet Relay Chat Protocol"""


from re import compile as compile_regex


from circuits import Component

from circuits.net.events import write
from circuits.protocols.line import Line


from .utils import parsemsg
from .message import Message
from .events import reply, response
from .commands import NOTICE, PONG, PRIVMSG, RAW


NUMERIC = compile_regex("[0-9]+")


class IRC(Component):
    """IRC Protocol Component

    Creates a new IRC Component instance that implements the IRC Protocol.
    Incoming messages are handled by the "read" Event Handler, parsed and
    processed with appropriate Events created and exposed to the rest of
    the system to listen to and handle.
    """

    def __init__(self, *args, **kwargs):
        super(IRC, self).__init__(*args, **kwargs)
        Line(**kwargs).register(self)

    def RAW(self, data):
        self.fire(write("%s\r\n" % data))

    def PASS(self, password):
        self.fire(RAW("PASS %s" % password))

    def AWAY(self, message=""):
        self.fire(RAW("AWAY :%s" % message))

    def USER(self, ident, host, server, name):
        self.fire(RAW("USER %s %s %s :%s" % (
            ident, host, server, name)))

    def NICK(self, nick):
        self.fire(RAW("NICK %s" % nick))

    def PING(self, server):
        self.fire(RAW("PING :%s" % server))

    def PONG(self, server):
        self.fire(RAW("PONG :%s" % server))

    def QUIT(self, message="Leaving"):
        self.fire(RAW("QUIT :%s" % message))

    def JOIN(self, channel, key=None):
        if key is None:
            self.fire(RAW("JOIN %s" % channel))
        else:
            self.fire(RAW("JOIN %s %s" % (channel, key)))

    def PART(self, channel, message="Leaving"):
        self.fire(RAW("PART %s :%s" % (channel, message)))

    def PRIVMSG(self, target, message):
        self.fire(RAW("PRIVMSG %s :%s" % (target, message)))

    def NOTICE(self, target, message):
        self.fire(RAW("NOTICE %s :%s" % (target, message)))

    def CTCP(self, target, type, message):
        self.fire(PRIVMSG(target, "%s %s" % (type, message)))

    def CTCPREPLY(self, target, type, message):
        self.fire(NOTICE(target, "%s %s" % (type, message)))

    def KICK(self, channel, target, message=""):
        self.fire(RAW("KICK %s %s :%s" % (channel, target, message)))

    def TOPIC(self, channel, topic):
        self.fire(RAW("TOPIC %s :%s" % (channel, topic)))

    def MODE(self, modes, channel=None):
        if channel is None:
            self.fire(RAW("MODE :%s" % modes))
        else:
            self.fire(RAW("MODE %s :%s" % (channel, modes)))

    def INVITE(self, target, channel):
        self.fire(RAW("INVITE %s %s" % (target, channel)))

    def NAMES(self, channel=None):
        if channel:
            self.fire(RAW("NAMES %s" % channel))
        else:
            self.fire(RAW("NAMES"))

    def WHOIS(self, nick):
        self.fire(RAW("WHOIS :%s" % nick))

    def line(self, *args):
        """line Event Handler

        Process a line of text and generate the appropriate
        event. This must not be overridden by subclasses,
        if it is, this must be explicitly called by the
        subclass. Other Components may however listen to
        this event and process custom IRC events.
        """

        if len(args) == 1:
            # Client read
            sock, line = None, args[0]
        else:
            # Server read
            sock, line = args

        prefix, command, args = parsemsg(line)

        command = command.lower().encode("utf-8")

        if NUMERIC.match(command):
            args.insert(0, int(command))
            command = "numeric"

        if sock is not None:
            self.fire(response.create(command, sock, prefix, *args))
        else:
            self.fire(response.create(command, prefix, *args))

    def ping(self, event, *args):
        """ping Event Handler (Default)

        This is a default event to respond to ``ping`` events
        by sending a ``PONG`` in response. Subclasses or
        components may override this, but be sure to respond to
        ``ping`` events by either explicitly calling this method
        or sending your own ``PONG`` response.
        """

        if len(args) == 2:
            # Client read
            self.fire(PONG(args[1]))
        else:
            # Server read
            self.fire(reply(args[0], Message("PONG", args[2])))

        event.stop()
