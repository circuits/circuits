"""Internet Relay Chat message"""


from circuits.six import text_type, u, PY3


from .utils import parsemsg


class Error(Exception):
    """Error Exception"""


class Message(object):

    def __init__(self, command, *args, **kwargs):
        for arg in args[:-1]:
            if u(" ") in arg:
                raise Error("Space can only appear in the very last arg")

        self.command = command
        self.args = list(filter(lambda x: x is not None, list(args)))
        self.prefix = text_type(kwargs["prefix"]) if "prefix" in kwargs else None

        self.encoding = kwargs.get("encoding", "utf-8")
        self.add_nick = kwargs.get("add_nick", False)

    @staticmethod
    def from_string(s):
        if len(s) > 512:
            raise Error("Message must not be longer than 512 characters")

        prefix, command, args = parsemsg(s)

        return Message(command, *args, prefix=prefix)

    def __str__(self):
        return self.__unicode__() if PY3 else self.__bytes__()

    def __bytes__(self):
        return text_type(self).encode(self.encoding)

    def __unicode__(self):
        args = self.args[:]
        for arg in args[:-1]:
            if arg is not None and u(" ") in arg:
                raise Error("Space can only appear in the very last arg")

        if len(args) > 0 and u(" ") in args[-1] and args[-1][0] != u(":"):
            args[-1] = u(":{0:s}").format(args[-1])

        return u("{prefix:s}{command:s} {args:s}\r\n").format(
            prefix=(
                u(":{0:s} ").format(self.prefix)
                if self.prefix is not None
                else u("")
            ),
            command=text_type(self.command),
            args=u(" ").join(args)
        )

    def __repr__(self):
        return repr(text_type(self)[:-2])

    def __eq__(self, other):
        return isinstance(other, Message) \
            and self.prefix == other.prefix \
            and self.command == other.command \
            and self.args == other.args
