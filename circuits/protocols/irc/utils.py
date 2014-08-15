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

    :param s str: string to process
    :param color bool: whether to strip colors

    :returns str: returns processes string
    """

    if len(s) > 0:
        if s[0] == ":":
            s = s[1:]
    if color:
        s = s.replace("\x01", "")
        s = s.replace("\x02", "")
    return s


def joinprefix(nick, user, host):
    """Join the parts of a prefix

    :param nick str: nickname
    :param user str: username
    :param host str: hostname

    :returns str: a string in the form of <nick>!<user>@<host>
    """

    return "{0:s}!{1:s}@{2:s}".format(nick or "", user or "", host or "")


def parseprefix(prefix):
    """Parse a prefix into it's parts

    :param prefix str: prefix to parse

    :returns tuple: tuple of strings in the form of (nick, user, host)
    """

    m = PREFIX.match(prefix)

    if m is not None:
        return m.groups()
    else:
        return prefix, None, None


def parsemsg(s, encoding="utf-8"):
    """Parse an IRC Message from s

    :param s bytes: bytes to parse
    :param encoding str: encoding to use (Default: utf-8)

    :returns tuple: parsed message in the form of (prefix, command, args)
    """

    s = s.decode(encoding)

    prefix = ""
    trailing = []

    if s[0] == ":":
        prefix, s = s[1:].split(" ", 1)

    prefix = parseprefix(prefix)

    if s.find(" :") != -1:
        s, trailing = s.split(" :", 1)
        args = s.split()
        args.append(trailing)
    else:
        args = s.split()

    command = str(args.pop(0))

    return prefix, command, args
