# Module:   utils
# Date:     11th August 2014
# Author:   James Mills <prologic@shortcircuit.net.au>


"""Internet Relay Chat Utilities"""


from re import compile as compile_regex


PREFIX = compile_regex("([^!].*)!(.*)@(.*)")


class Error(Exception):
    """Error Exception"""


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


def joinprefix(nick, user, host):
    """Join the parts of a prefix"""

    return "{0:s}!{1:s}@{2:s}".format(nick, user, host)


def parseprefix(prefix):
    """Parse a prefix into it's parts"""

    m = PREFIX.match(prefix)

    if m is not None:
        return m.groups()
    else:
        return prefix, None, None


def parsemsg(s):
    """Parse an IRC Message from s"""

    if not s:
        raise Error("Empty line!")

    prefix = ""
    trailing = []

    if s[0] == ":":
        prefix, s = s[1:].split(" ", 1)

    if s.find(" :") != -1:
        s, trailing = s.split(" :", 1)
        args = s.split()
        args.append(trailing)
    else:
        args = s.split()

    command = args.pop(0)

    return parseprefix(prefix), command, args
