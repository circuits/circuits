# Module:   commands
# Date:     11th August 2014
# Author:   James Mills <prologic@shortcircuit.net.au>


"""Internet Relay Chat Protocol commands"""


from circuits import Event


class command(Event):
    """command Event"""


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
