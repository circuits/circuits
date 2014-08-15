# Module:   message
# Date:     11th August 2014
# Author:   James Mills <prologic@shortcircuit.net.au>


"""Internet Relay Chat message"""


from .utils import parsemsg


class Error(Exception):
    """Error Exception"""


class Message(object):

    def __init__(self, command, *args, **kwargs):
        for arg in args[:-1]:
            if " " in arg:
                raise Error("Space can only appear in the very last arg")

        self.command = command
        self.args = list(filter(lambda x: x is not None, list(args)))
        self.prefix = str(kwargs["prefix"]) if "prefix" in kwargs else None

        self.encoding = kwargs.get("encoding", "utf-8")
        self.add_nick = kwargs.get("add_nick", False)

    @staticmethod
    def from_string(s):
        if len(s) > 512:
            raise Error("Message must not be longer than 512 characters")

        prefix, command, args = parsemsg(s)

        return Message(command, *args, prefix=prefix)

    def __bytes__(self):
        return str(self).encode(self.encoding)

    def __str__(self):
        args = self.args[:]
        for arg in args[:-1]:
            if arg is not None and " " in arg:
                raise Error("Space can only appear in the very last arg")

        if len(args) > 0 and " " in args[-1]:
            args[-1] = ":{0:s}".format(args[-1])

        return "{prefix:s}{command:s} {args:s}\r\n".format(
            prefix=(
                ":{0:s} ".format(self.prefix)
                if self.prefix is not None
                else ""
            ),
            command=str(self.command),
            args=" ".join(args)
        )

    def __repr__(self):
        return "\"{0:s}\"".format(str(self)[:-2])

    def __eq__(self, other):
        return isinstance(other, Message) \
            and self.prefix == other.prefix \
            and self.command == other.command \
            and self.args == other.args
