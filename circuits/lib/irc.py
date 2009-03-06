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
import time

from circuits.lib.sockets import Write
from circuits import Event, Component

###
### Supporting Functions
###

LINESEP = re.compile("\r?\n")

def splitLines(s, buffer):
    """splitLines(s, buffer) -> lines, buffer

    Append s to buffer and find any new lines of text in the
    string splitting at the standard IRC delimiter CRLF. Any
    new lines found, return them as a list and the remaining
    buffer for further processing.
    """

    lines = LINESEP.split(buffer + s)
    return lines[:-1], lines[-1]

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

    Split the given source into it's parts.

    source must be of the form: nick!ident@host

    Example:
    >>> nick, ident, host, = sourceSplit("Joe!Blogs@localhost")
    """

    m = re.match(
            "(?P<nick>[^!].*)!(?P<ident>.*)@(?P<host>.*)",
            source)

    if m is not None:
        d = m.groupdict()
        return d["nick"], d["ident"], d["host"]
    else:
        return source, None, None

###
### Evenets
###

class Raw(Event):
    """Raw(Event) -> Raw Event

   args: line
   """

class Numeric(Event):
    """Numeric(Event) -> Numeric Event

   args: source, target, numeric, arg, message
   """

class NewNick(Event):
    """NewNick(Event) -> NewNick Event

   (Server mode only)
   """

class Pass(Event): pass
class User(Event): pass

class Nick(Event):
    """Nick(Event) -> Nick Event

    args: source, newnick, ctime
    """

class Quit(Event):
    """Quit(Event) -> Quit Event

   args: source, message
   """

class Message(Event):
    """Message(Event) -> Message Event

   args: source, target, message
   """

class Notice(Event):
    """Notice(Event) -> Notice Event

   args: source, target, message
   """

class Ping(Event):
    """Ping(Event) -> Ping Event

   args: server
   """

class Pong(Event):
    """Pong(Event) -> Pong Event

   args: source daemon [daemon2]
   """

class Join(Event):
    """Join(Event) -> Join Event

   args: source, channel
   """

class Part(Event):
    """Part(Event) -> Part Event

   args: source, channel, message
   """

class Ctcp(Event):
    """Ctcp(Event) -> Ctcp Event

   args: source, target, type, message
   """

class Topic(Event):
    """Topic(Event) -> Topic Event

   args: source, channel, ctime, topic
   """

class NetInfo(Event):
    """NetINfo(Event) -> NetInfo Event

   args: ...
   """

###
### Protocol Class
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
        self._data = ""
        self._info = {}

        super(IRC, self).__init__(*args, **kwargs)

    ###
    ### Properties
    ###

    def getNick(self):
        """I.getNick() -> str

        Return the current nickname if set,
        return None otherwise.
        """

        return self._info.get("nick", None)

    def getIdent(self):
        """I.getIdent() -> str

        Return the current ident if set,
        return None otherwise.
        """

        return self._info.get("ident", None)

    def getHost(self):
        """I.getHost() -> str

        Return the current host if set,
        return None otherwise.
        """

        return self._info.get("host", None)

    def getServer(self):
        """I.getServer() -> str

        Return the current server if set,
        return None otherwise.
        """

        return self._info.get("server", None)

    def getServerVersion(self):
        """I.getServerVersion() -> str

        Return the current server version if set,
        return None otherwise.
        """

        return self._info.get("serverVersion", None)

    def getNetwork(self):
        """I.getNetwork() -> str

        Return the current network if set,
        return None otherwise.
        """

        return self._info.get("network", None)

    def getName(self):
        """I.getName() -> str

        Return the current name if set,
        return None otherwise.
        """

        return self._info.get("name", None)

    ###
    ### IRC Commands
    ###

    def RAW(self, data):
        self.push(Write("%s\r\n" % data), "write", self.channel)

    def PASS(self, password):
        self.RAW("PASS %s" % password)

    def SERVER(self, server, hops, token, description):
         self.RAW("SERVER %s %s %s :%s" % (server, hops,
             token, description))

    def USER(self, ident, host, server, name):
        self.RAW("USER %s \"%s\" \"%s\" :%s" % (
            ident, host, server, name))
        self._info["ident"] = ident
        self._info["host"] = host
        self._info["server"] = server
        self._info["name"] = name

    def NICK(self, nick, idle=None, signon=None, ident=None,
            host=None, server=None, hops=None, name=None):

        if reduce(lambda x, y: x is not None and y is not None, [
            idle, signon, ident, host, server, hops, name]):

            self.RAW("NICK %s %d %d %s %s %s %d :%s" % (
                nick, idle, signon, ident, host, server,
                hops, name))

        else:
            self.RAW("NICK %s" % nick)
            self._info["nick"] = nick

    def PING(self, server):
        self.RAW("PING :%s" % server)

    def PONG(self, server):
        self.RAW("PONG :%s" % server)

    def QUIT(self, message="", source=None):
        if source is None:
            self.RAW("QUIT :%s" % message)
        else:
            self.RAW(":%s QUIT :%s" % (source, message))

    def JOIN(self, channel, key=None, source=None):
        if source is None:
            if key is None:
                self.RAW("JOIN %s" % channel)
            else:
                self.RAW("JOIN %s %s" % (channel, key))
        else:
            if key is None:
                self.RAW(":%s JOIN %s" % (source, channel))
            else:
                self.RAW(":%s JOIN %s %s" % (source,
                    channel, key))

    def PART(self, channel, message="", source=None):
        if source is None:
            self.RAW("PART %s :%s" % (channel, message))
        else:
            self.RAW(":%s PART %s :%s" % (source, channel,
                message))

    def PRIVMSG(self, target, message, source=None):
        if source is None:
            self.RAW("PRIVMSG %s :%s" % (target, message))
        else:
            self.RAW(":%s PRIVMSG %s :%s" % (source,
                target, message))

    def NOTICE(self, target, message, source=None):
        if source is None:
            self.RAW("NOTICE %s :%s" % (target, message))
        else:
            self.RAW(":%s NOTICE %s :%s" % (source,
                target, message))

    def CTCP(self, target, type, message, source=None):
        self.PRIVMSG(target, "%s %s" % (type, message),
                source)

    def CTCPREPLY(self, target, type, message, source=None):
        self.NOTICE(target, "%s %s" % (type, message),
              source)

    def KICK(self, channel, target, message="", source=None):
        if source is None:
            self.RAW("KICK %s %s :%s" % (channel, target,
                message))
        else:
            self.RAW(":%s KICK %s %s :%s" % (source, channel,
                target, message))

    def TOPIC(self, channel, topic, whoset=None,
            whenset=None, source=None):
        if source is None:
            if whoset is None and whenset is None:
                self.RAW("TOPIC %s :%s" % (channel, topic))
            else:
                self.RAW("TOPIC %s %s %d :%s" % (channel,
                    whoset, whenset, topic)),
        else:
            if whoset is None and whenset is None:
                self.RAW(":%s TOPIC %s :%s" % (source,
                    channel, topic))
            else:
                self.RAW(":%s TOPIC %s %s %d :%s" % (source,
                    channel, whoset, whenset, topic)),

    def MODE(self, modes, channel=None, source=None):
        if source is None:
            if channel is None:
                self.MODE("MODE :%s" % modes)
            else:
                self.MODE("MODE %s :%s" % (channel, modes))
        else:
            if channel is None:
                self.MODE(":%s MODE :%s" % (source, modes))
            else:
                self.MODE(":%s MODE %s :%s" % (source, channel,
                    modes))

    def KILL(self, target, message):
        self.RAW("KILL %s :%s" % (target, message))

    def INVITE(self, target, channel, source=None):
        if source is None:
            self.RAW("INVITE %s %s" % (target, channel))
        else:
            self.RAW(":%s INVITE %s %s" % (source, target,
                channel))

    def NAMES(self, channel=None):
        if channel:
            self.RAW("NAMES %s" % channel)
        else:
            self.RAW("NAMES")

    ###
    ### Properties
    ###

    nick = property(getNick, NICK)

    ###
    ### Event Processing
    ###

    def read(self, data):
        """Read Event Handler

           Process any incoming data appending it to an internal
           buffer. Split the buffer by the standard IRC delimiter
           CRLF and create a Raw event per line. Any unfinished
           lines of text, leave in the buffer.
        """

        lines, self._data = splitLines(data, self._data)
        for line in lines:
            self.push(Raw(line), "raw", self.channel)

    def raw(self, line):
        """I.onRAW(line) -> None

        Process a line of text and generate the appropiate
        event. This must not be overridden by sub-classes,
        if it is, this must be explitetly called by the
        sub-class. Other Components may however listen to
        this event and process custom IRC events.
        """

        tokens = line.split(" ")

        if tokens[0] == "PING":
            self.push(Ping(strip(tokens[1]).lower()), "ping", self.channel)

        elif tokens[0] == "NICK":
            self.push(NewNick(
                    tokens[1].lower(), int(tokens[2]),
                    int(tokens[3]), tokens[4].lower(),
                    tokens[5].lower(), tokens[6].lower(),
                    strip(" ".join(tokens[8:]))),
                    "newnick", self.channel)

        elif tokens[0] == "TOPIC":
            self.push(Topic(
                    tokens[1], tokens[2], int(tokens[3]),
                    strip(" ".join(tokens[4:]))),
                    "topic", self.channel)

        elif tokens[0] == "NETINFO":
            self.push(NetInfo(
                    int(tokens[1]),
                    int(tokens[2]),
                    tokens[3],
                    tokens[4],
                    tokens[5],
                    tokens[6],
                    tokens[7],
                    strip(" ".join(tokens[8:]))),
                    "netinfo", self.channel)

        elif re.match("[0-9]+", tokens[1]):
            source = sourceSplit(strip(tokens[0].lower()))
            target = tokens[2].lower()

            numeric = int(tokens[1])
            if len(tokens[3]) > 1:
                if tokens[3][0] == ":":
                    arg = None
                    message = strip(" ".join(tokens[3:]))
                else:
                    arg = tokens[3]
                    message = strip(" ".join(tokens[4:]))
            else:
                arg = None
                message = strip(" ".join(tokens[4:]))

            if numeric == RPL_WELCOME:
                """
                Welcome to the UnderNet IRC Network, kdb

                Welcome to the Internet Relay Network kdb!-kdb@202.63.43.101

                Welcome to the GameSurge IRC Network via burstfire.net, prologic
                """

                m = re.match(
                        "Welcome to the (?P<network>.*) "
                        "(IRC|Internet Relay( Chat)?) Network "
                        "(?P<user>.*)", message)

                if m is None:
                    m = re.match(
                            "Welcome to the Internet Relay Network "
                            "(?P<user>.*)", message)

                if m is None:
                    m = re.match(
                            "Welcome to the (?P<network>.*) "
                            "IRC Network, "
                            "(?P<user>.*)", message)

                d = m.groupdict()

                nick, ident, host = sourceSplit(d["user"])
                self._info["network"] = d.get("network", "")
                self._info["nick"] = nick
                if ident is not None:
                    self._info["ident"] = ident
                if host is not None:
                    self._info["host"] = host
            elif numeric == RPL_YOURHOST:
                tokens = message.split(" ")
                self._info["server"] = tokens[3].rstrip(",")
                self._info["serverVersion"] = tokens[6]

            self.push(Numeric(
                    source, target, numeric, arg, message),
                    "numeric", self.channel)

        elif tokens[1] == "PRIVMSG":
            source = sourceSplit(strip(tokens[0].lower()))
            target = tokens[2].lower()
            message = strip(" ".join(tokens[3:]))

            if not message == "":
                if message[0] == "":
                    tokens = strip(message, color=True).split(" ")
                    type = tokens[0].lower()
                    message = " ".join(tokens[1:])
                    self.push(Ctcp(
                            source, target, type, message),
                            "ctcp", self.channel)
                else:
                    self.push(Message(
                            source, target, message),
                            "message", self.channel)
            else:
                self.push(Message(
                        source, target, message),
                        "message", self.channel)

        elif tokens[1] == "NOTICE":
            source = sourceSplit(strip(tokens[0].lower()))
            target = tokens[2].lower()
            message = strip(" ".join(tokens[3:]))
            self.push(Notice(
                    source, target, message),
                    "notice", self.channel)

        elif tokens[1] == "JOIN":
            source = sourceSplit(strip(tokens[0].lower()))
            channels = strip(tokens[2]).lower()
            for channel in channels.split(","):
                self.push(Join(
                        source, channel),
                        "join", self.channel)

        elif tokens[1] == "PART":
            source = sourceSplit(strip(tokens[0].lower()))
            channel = strip(tokens[2]).lower()
            message = strip(" ".join(tokens[3:]))
            self.push(Part(
                    source, channel, message),
                    "part", self.channel)

        elif tokens[1] == "QUIT":
            source = sourceSplit(strip(tokens[0].lower()))
            message = strip(" ".join(tokens[2:]))
            self.push(Quit(
                    source, message),
                    "quit", self.channel)

        elif tokens[1] == "NICK":
            source = sourceSplit(strip(tokens[0].lower()))
            newNick = strip(tokens[2]).lower()

            if self.getNick() is not None:
                if source.lower() == self.getNick().lower():
                    self._info["nick"] = newNick

            if len(tokens) == 4:
                ctime = strip(tokens[3])
            else:
                ctime = time.time()

            self.push(Nick(
                    source, newNick, ctime),
                    "nick", self.channel)

        elif tokens[1] == "PONG":
            source = sourceSplit(strip(tokens[0].lower()))
            args = [strip(x) for x in tokens[2:]]
            self.push(Pong(source, *args), "pong", self.channel)

    ###
    ### Default Events
    ###

    def ping(self, server):
        """Ping Event

        This is a default event ro respond to Ping Events
        by sending out a Pong in response. Sub-classes
        may override this, but be sure to respond to
        Ping Events by either explitetly calling this method
        or sending your own Pong reponse.
        """

        self.push(Pong(server), "PONG", self.channel)

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
