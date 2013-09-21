# Module:   irc
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Internet Relay Chat Protocol

This module implements the Internet Relay Chat Protocol
or commonly known as IRC.

This module can be used in both server and client
implementations.
"""

import re

from circuits.net.sockets import Write
from circuits.core import handler, Event, DerivedEvent, Component

from .line import LP

###
### Supporting Functions
###


def strip(s, color=False):
    """strip(s, color=False) -> str

    Strips the : from the start of a string
    and optionally also strips all colors if
    color is True.
    """

    if len(s) > 0:
        if s[0] == ":":
            s = s[1:]
    if color:
        s = s.replace("\x01", "")
        s = s.replace("\x02", "")
    return s


def sourceJoin(nick, ident, host):
    """sourceJoin(nick, ident, host) -> str

    Join a source previously split by sourceSplit
    and join it back together inserting the ! and @
    appropiately.
    """

    return "%s!%s@%s" % (nick, ident, host)


def sourceSplit(source):
    """sourceSplit(source) -> str, str, str

    Split the given source into its parts.

    source must be of the form: nick!ident@host

    Example:
    >>> nick, ident, host, = sourceSplit("Joe!Blogs@localhost")
    """

    m = re.match(
        "(?P<nick>[^!].*)!(?P<ident>.*)@(?P<host>.*)",
        source
    )

    if m is not None:
        d = m.groupdict()
        return d["nick"], d["ident"], d["host"]
    else:
        return source, None, None

###
### IRC Commands
###


class command(DerivedEvent):
    """command DerivedEvent"""


class AWAY(command):
    """AWAY command"""


class RAW(command):
    """RAW command"""


class PASS(command):
    """PASS command"""


class USER(command):
    """USER command"""


class NICK(command):
    """NICK command"""


class PING(command):
    """PING command"""


class PONG(command):
    """PONG command"""


class QUIT(command):
    """QUIT command"""


class JOIN(command):
    """JOIN command"""


class PART(command):
    """PART command"""


class PRIVMSG(command):
    """PRIVMSG command"""


class NOTICE(command):
    """NOTICE command"""


class CTCP(command):
    """CTCP command"""


class CTCPREPLY(command):
    """CTCPREPLY command"""


class KICK(command):
    """KICK command"""


class TOPIC(command):
    """TOPIC command"""


class MODE(command):
    """MODE command"""


class INVITE(command):
    """INVITE command"""


class NAMES(command):
    """NAMES command"""


class WHOIS(command):
    """WHOIS command"""

###
### IRC Responses
###


class response(Event):
    """response Event"""


class numeric(response):
    """numeric response"""


class away(response):
    """Target user is away."""


class ping(response):
    """ping response"""


class ctcp(response):
    """ctcp response"""


class message(response):
    """message response"""


class notice(response):
    """notice response"""


class join(response):
    """join response"""


class part(response):
    """part response"""


class quit(response):
    """quit response"""


class nick(response):
    """nick response"""


class mode(response):
    """mode response"""


class invite(response):
    """invite response"""


###
### Protocol Component(s)
###


class IRC(Component):
    """IRC Protocol Component

    Creates a new IRC Component instance that implements the IRC Protocol.
    Incoming messages are handled by the "read" Event Handler, parsed and
    processed with appropriate Events created and exposed to the rest of
    te system to listen to and handle.

    @note: This Component must be used in conjunction with a Component that
           exposes Read Events on a "read" Channel.
    """

    def __init__(self, *args, **kwargs):
        super(IRC, self).__init__(*args, **kwargs)
        LP(**kwargs).register(self)

    ###
    ### IRC Command Event Handlers
    ###

    def command_RAW(self, data):
        self.fire(Write("%s\r\n" % data))

    def command_PASS(self, password):
        self.fire(RAW("PASS %s" % password))

    def command_AWAY(self, message=""):
        self.fire(RAW("AWAY :%s" % message))

    def command_USER(self, ident, host, server, name):
        self.fire(RAW("USER %s \"%s\" \"%s\" :%s" % (
            ident, host, server, name)))

    def command_NICK(self, nick):
        self.fire(RAW("NICK %s" % nick))

    def command_PING(self, server):
        self.fire(RAW("PING :%s" % server))

    def command_PONG(self, server):
        self.fire(RAW("PONG :%s" % server))

    def command_QUIT(self, message="Leaving"):
        self.fire(RAW("QUIT :%s" % message))

    def command_JOIN(self, channel, key=None):
        if key is None:
            self.fire(RAW("JOIN %s" % channel))
        else:
            self.fire(RAW("JOIN %s %s" % (channel, key)))

    def command_PART(self, channel, message="Leaving"):
        self.fire(RAW("PART %s :%s" % (channel, message)))

    def command_PRIVMSG(self, target, message):
        self.fire(RAW("PRIVMSG %s :%s" % (target, message)))

    def command_NOTICE(self, target, message):
        self.fire(RAW("NOTICE %s :%s" % (target, message)))

    def command_CTCP(self, target, type, message):
        self.fire(PRIVMSG(target, "%s %s" % (type, message)))

    def command_CTCPREPLY(self, target, type, message):
        self.fire(NOTICE(target, "%s %s" % (type, message)))

    def command_KICK(self, channel, target, message=""):
        self.fire(RAW("KICK %s %s :%s" % (channel, target, message)))

    def command_TOPIC(self, channel, topic):
        self.fire(RAW("TOPIC %s :%s" % (channel, topic)))

    def command_MODE(self, modes, channel=None):
        if channel is None:
            self.fire(RAW("MODE :%s" % modes))
        else:
            self.fire(RAW("MODE %s :%s" % (channel, modes)))

    def command_INVITE(self, target, channel):
        self.fire(RAW("INVITE %s %s" % (target, channel)))

    def command_NAMES(self, channel=None):
        if channel:
            self.fire(RAW("NAMES %s" % channel))
        else:
            self.fire(RAW("NAMES"))

    def command_WHOIS(self, nick):
        self.fire(RAW("WHOIS :%s" % nick))

    ###
    ### Event Processing
    ###

    def line(self, line):
        """Line Event Handler

        Process a line of text and generate the appropiate
        event. This must not be overridden by sub-classes,
        if it is, this must be explitetly called by the
        sub-class. Other Components may however listen to
        this event and process custom IRC events.
        """

        tokens = line.split(" ")

        if tokens[0] == "PING":
            self.fire(ping(strip(tokens[1])))

        elif re.match("[0-9]+", tokens[1]):
            source = strip(tokens[0])
            target = tokens[2]

            n = int(tokens[1])

            if tokens[3].startswith(":"):
                arg = None
                message = strip(" ".join(tokens[3:]))
            else:
                arg = tokens[3]
                message = strip(" ".join(tokens[4:]))

            self.fire(numeric(source, target, n, arg, message))

            if n == 301:
                self.fire(away(arg, message))

        elif tokens[1] == "PRIVMSG":
            source = sourceSplit(strip(tokens[0]))
            target = tokens[2]
            message = strip(" ".join(tokens[3:]))

            if message and message[0] == "":
                tokens = strip(message, color=True).split(" ")
                type = tokens[0]
                message = " ".join(tokens[1:])
                self.fire(ctcp(source, target, type, message))
            else:
                self.fire(message(source, target, message))

        elif tokens[1] == "NOTICE":
            source = sourceSplit(strip(tokens[0]))
            target = tokens[2]
            message = strip(" ".join(tokens[3:]))
            self.fire(notice(source, target, message))

        elif tokens[1] == "JOIN":
            source = sourceSplit(strip(tokens[0]))
            channel = strip(tokens[2])
            self.fire(join(source, channel))

        elif tokens[1] == "PART":
            source = sourceSplit(strip(tokens[0]))
            channel = strip(tokens[2])
            message = strip(" ".join(tokens[3:]))
            self.fire(part(source, channel, message))

        elif tokens[1] == "QUIT":
            source = sourceSplit(strip(tokens[0]))
            message = strip(" ".join(tokens[2:]))
            self.fire(quit(source, message))

        elif tokens[1] == "NICK":
            source = sourceSplit(strip(tokens[0]))
            newNick = strip(tokens[2])

            self.fire(nick(source, newNick))

        elif tokens[1] == "MODE":
            source = sourceSplit(strip(tokens[0]))
            target = tokens[2]
            modes = strip(" ".join(tokens[3:]))
            self.fire(mode(source, target, modes))
        elif tokens[1] == "INVITE":
            source = sourceSplit(strip(tokens[0]))
            target = tokens[2]
            channel = strip(tokens[3])
            self.fire(invite(source, target, channel))

    ###
    ### Default Events
    ###

    @handler("ping", filter=True)
    def _on_ping(self, event, server):
        """Ping Event

        This is a default event ro respond to Ping Events
        by sending out a Pong in response. Sub-classes
        may override this, but be sure to respond to
        Ping Events by either explitetly calling this method
        or sending your own Pong reponse.
        """

        if isinstance(event, ping):
            self.fire(PONG(server))
            return True

###
### Errors and Numeric Replies
###

RPL_WELCOME = 1
RPL_YOURHOST = 2

RPL_TRACELINK = 200
RPL_TRACECONNECTING = 201
RPL_TRACEHANDSHAKE = 202
RPL_TRACEUNKNOWN = 203
RPL_TRACEOPERATOR = 204
RPL_TRACEUSER = 205
RPL_TRACESERVER = 206
RPL_TRACENEWTYPE = 208
RPL_TRACELOG = 261
RPL_STATSLINKINFO = 211
RPL_STATSCOMMANDS = 212
RPL_STATSCLINE = 213
RPL_STATSNLINE = 214
RPL_STATSILINE = 215
RPL_STATSKLINE = 216
RPL_STATSYLINE = 218
RPL_ENDOFSTATS = 219
RPL_STATSLLINE = 241
RPL_STATSUPTIME = 242
RPL_STATSOLINE = 243
RPL_STATSHLINE = 244
RPL_UMODEIS = 221
RPL_LUSERCLIENT = 251
RPL_LUSEROP = 252
RPL_LUSERUNKNOWN = 253
RPL_LUSERCHANNELS = 254
RPL_LUSERME = 255
RPL_ADMINME = 256
RPL_ADMINLOC1 = 257
RPL_ADMINLOC2 = 258
RPL_ADMINEMAIL = 259

RPL_NONE = 300
RPL_USERHOST = 302
RPL_ISON = 303
RPL_AWAY = 301
RPL_UNAWAY = 305
RPL_NOWAWAY = 306
RPL_WHOISUSER = 311
RPL_WHOISSERVER = 312
RPL_WHOISOPERATOR = 313
RPL_WHOISIDLE = 317
RPL_ENDOFWHOIS = 318
RPL_WHOISCHANNELS = 319
RPL_WHOWASUSER = 314
RPL_ENDOFWHOWAS = 369
RPL_LIST = 322
RPL_LISTEND = 323
RPL_CHANNELMODEIS = 324
RPL_NOTOPIC = 331
RPL_TOPIC = 332
RPL_INVITING = 341
RPL_SUMMONING = 342
RPL_VERSION = 351
RPL_WHOREPLY = 352
RPL_ENDOFWHO = 315
RPL_NAMREPLY = 353
RPL_ENDOFNAMES = 366
RPL_LINKS = 364
RPL_ENDOFLINKS = 365
RPL_BANLIST = 367
RPL_ENDOFBANLIST = 368
RPL_INFO = 371
RPL_ENDOFINFO = 374
RPL_MOTDSTART = 375
RPL_MOTD = 372
RPL_ENDOFMOTD = 376
RPL_YOUREOPER = 381
RPL_REHASHING = 382
RPL_TIME = 391
RPL_USERSSTART = 392
RPL_USERS = 393
RPL_ENDOFUSERS = 394
RPL_NOUSERS = 395

ERR_NOSUCHNICK = 401
ERR_NOSUCHSERVER = 402
ERR_NOSUCHCHANNEL = 403
ERR_CANNOTSENDTOCHAN = 404
ERR_TOOMANYCHANNELS = 405
ERR_WASNOSUCHNICK = 406
ERR_TOOMANYTARGETS = 407
ERR_NOORIGIN = 409
ERR_NORECIPIENT = 411
ERR_NOTEXTTOSEND = 412
ERR_NOTOPLEVEL = 413
ERR_WILDTOPLEVEL = 414
ERR_UNKNOWNCOMMAND = 421
ERR_NOMOTD = 422
ERR_NOADMININFO = 423
ERR_FILEERROR = 424
ERR_NONICKNAMEGIVEN = 431
ERR_ERRONEUSNICKNAME = 432
ERR_NICKNAMEINUSE = 433
ERR_NICKCOLLISION = 436
ERR_NOTONCHANNEL = 442
ERR_USERONCHANNEL = 443
ERR_NOLOGIN = 444
ERR_SUMMONDISABLED = 445
ERR_USERSDISABLED = 446
ERR_NOTREGISTERED = 451
ERR_NEEDMOREPARAMS = 461
ERR_ALREADYREGISTRED = 462
ERR_PASSWDMISMATCH = 464
ERR_YOUREBANNEDCREEP = 465
ERR_KEYSET = 467
ERR_CHANNELISFULL = 471
ERR_UNKNOWNMODE = 472
ERR_INVITEONLYCHAN = 473
ERR_BANNEDFROMCHAN = 474
ERR_BADCHANNELKEY = 475
ERR_NOPRIVILEGES = 481
ERR_CHANOPRIVSNEEDED = 482
ERR_CANTKILLSERVER = 483
ERR_NOOPERHOST = 491

ERR_UMODEUNKNOWNFLAG = 501
ERR_USERSDONTMATCH = 502
