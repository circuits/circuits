"""Internet Relay Chat Utilities"""


from re import compile as compile_regex

from circuits.six import u

PREFIX = compile_regex("([^!].*)!(.*)@(.*)")
COLOR_CODE = compile_regex(r'(?:(\d\d?)(?:(,)(\d\d?))?)?')
COLOR = compile_regex(r"\x03(?:(\d\d?)(?:,(\d\d?))?)?")


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
        s = s.replace(u("\x02"), u(""))  # bold
        s = s.replace(u("\x1d"), u(""))  # italics
        s = s.replace(u("\x1f"), u(""))  # underline
        s = s.replace(u("\x1e"), u(""))  # strikethrough
        s = s.replace(u("\x11"), u(""))  # monospace
        s = s.replace(u("\x16"), u(""))  # reverse color
        s = COLOR.sub(u(""), s)  # color codes
        s = s.replace(u("\x03"), u(""))  # color
        s = s.replace(u("\x0f"), u(""))  # reset
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


def irc_color_to_ansi(data, reset=True):
    """Maps IRC color codes to ANSI terminal escape sequences"""

    def ansi(*seq):
        return u("\33[{}m").format(u(";").join(u("{:02}").format(x) for x in seq if x))

    ansi_default_fg = 39
    ansi_default_bg = 49
    color_map_fg = {
        0: 37, 1: 30, 2: 34, 3: 32, 4: 31, 5: 36, 6: 35, 7: 33, 8: 93, 9: 92,
        10: 36, 11: 96, 12: 94, 13: 95, 14: 90, 15: 37,
        16: 52, 17: 94, 18: 100, 19: 58, 20: 22, 21: 29, 22: 23, 23: 24,
        24: 17, 25: 54, 26: 53, 27: 89, 28: 88, 29: 130, 30: 142, 31: 64,
        32: 28, 33: 35, 34: 30, 35: 25, 36: 18, 37: 91, 38: 90, 39: 125,
        40: 124, 41: 166, 42: 184, 43: 106, 44: 34, 45: 49, 46: 37, 47: 33,
        48: 19, 49: 129, 50: 127, 51: 161, 52: 196, 53: 208, 54: 226,
        55: 154, 56: 46, 57: 86, 58: 51, 59: 75, 60: 21, 61: 171, 62: 201,
        63: 198, 64: 203, 65: 215, 66: 227, 67: 191, 68: 83, 69: 122, 70: 87,
        71: 111, 72: 63, 73: 177, 74: 207, 75: 205, 76: 217, 77: 223, 78: 229,
        79: 193, 80: 157, 81: 158, 82: 159, 83: 153, 84: 147, 85: 183, 86: 219,
        87: 212, 88: 16, 89: 233, 90: 235, 91: 237, 92: 239, 93: 241, 94: 244,
        95: 247, 96: 250, 97: 254, 98: 231, 99: ansi_default_fg
    }
    color_map_bg = {
        0: 47, 1: 40, 2: 44, 3: 42, 4: 41, 5: 46, 6: 45, 7: 43, 8: 103, 10: 46, 14: 97, 15: 47, 99: ansi_default_bg
    }

    enable_char = {
        u('\x16'): 1, u('\x1d'): 3, u('\x1e'): 9, u('\x1f'): 4, u('\x16'): 7
    }
    revert_char = {
        u('\x02'): 22, u('\x1d'): 23, u('\x1f'): 24, u('\x16'): 27, u('\x1e'): 29
    }

    def escape(data):
        ignore = set()
        start = []
        current_fg = ansi_default_fg
        current_bg = ansi_default_bg
        for i, char in enumerate(data):
            if i in ignore:
                continue
            if char == u('\x0f'):  # reset
                start = []
                yield ansi(0)
            elif char in start and char in revert_char:
                start.remove(char)
                yield ansi(revert_char[char])
            elif char in enable_char:
                start.append(char)
                yield ansi(enable_char[char])
            elif char == u('\x03'):
                i += 1
                m = COLOR_CODE.match(data[i:i + 5])
                colors = []
                if m:
                    fg, has_bg, bg = m.groups()
                    if fg:
                        ignore.update(range(i, i + len(fg)))
                        colors.append(color_map_fg.get(int(fg), current_fg))
                        current_fg = int(fg)
                    if has_bg:
                        ignore.update(range(i + len(fg), i + len(fg) + 1))
                    if bg:
                        ignore.update(range(i + len(fg) + 1, i + len(fg) + 1 + len(bg)))
                        colors.append(color_map_bg.get(int(bg), current_bg))
                        current_bg = int(bg)
                if char in start:
                    start.remove(char)
                if colors:
                    start.append(char)
                    yield ansi(*colors)
                else:
                    yield ansi(ansi_default_fg, ansi_default_bg)
            #elif char == u('\x04'):
            #    if char[i + 1:i + 6].isdigit():
            #        ignore.update(range(i, i + 6))
            #    # TODO: parse hex representation
            #elif char == u('\x11'):  # monospace
            #    start.append(char)
            else:
                yield char
        if start and reset:
            yield ansi(0)
    return u("").join(escape(data))
