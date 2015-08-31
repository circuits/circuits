"""Internet Relay Chat Utilities"""


from re import compile as compile_regex


from circuits.six import u


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
        if s[0] == u(":"):
            s = s[1:]
    if color:
        s = s.replace(u("\x01"), u(""))
        s = s.replace(u("\x02"), u(""))
    return s


def joinprefix(nick, user, host):
    """Join the parts of a prefix

    :param nick str: nickname
    :param user str: username
    :param host str: hostname

    :returns str: a string in the form of <nick>!<user>@<host>
    """

    return u("{0}!{1}@{2}").format(nick or u(""), user or u(""), host or u(""))


def parseprefix(prefix):
    """Parse a prefix into it's parts

    :param prefix str: prefix to parse

    :returns tuple: tuple of strings in the form of (nick, user, host)
    """

    m = PREFIX.match(prefix)

    if m is not None:
        return m.groups()
    else:
        return prefix or None, None, None


def parsemsg(s, encoding="utf-8"):
    """Parse an IRC Message from s

    :param s bytes: bytes to parse
    :param encoding str: encoding to use (Default: utf-8)

    :returns tuple: parsed message in the form of (prefix, command, args)
    """

    s = s.decode(encoding, 'replace')

    prefix = u("")
    trailing = []

    if s and s[0] == u(":"):
        prefix, s = s[1:].split(u(" "), 1)

    prefix = parseprefix(prefix)

    if s.find(u(" :")) != -1:
        s, trailing = s.split(u(" :"), 1)
        args = s.split()
        args.append(trailing)
    else:
        args = s.split()

    args = iter(args)
    command = next(args, None)
    command = command and str(command)

    return prefix, command, list(args)
