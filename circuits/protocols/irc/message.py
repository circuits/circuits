"""Internet Relay Chat message"""

from .utils import parsemsg


class Error(Exception):
    """Error Exception"""


class Message:
    def __init__(self, command, *args, **kwargs):
        self.command = command
        self.prefix = str(kwargs['prefix']) if 'prefix' in kwargs else None

        self.encoding = kwargs.get('encoding', 'utf-8')
        self.add_nick = kwargs.get('add_nick', False)
        self.args = [arg if isinstance(arg, str) else arg.decode(self.encoding) for arg in args if arg is not None]
        self._check_args()

    def _check_args(self):
        if any(type(arg)(' ') in arg in arg for arg in self.args[:-1] if isinstance(arg, str)):
            raise Error('Space can only appear in the very last arg')
        if any(type(arg)('\n') in arg for arg in self.args if isinstance(arg, str)):
            raise Error('No newline allowed')

    @staticmethod
    def from_string(s):
        if len(s) > 512:
            raise Error('Message must not be longer than 512 characters')

        prefix, command, args = parsemsg(s)

        return Message(command, *args, prefix=prefix)

    def __bytes__(self):
        return str(self).encode(self.encoding)

    def __str__(self):
        self._check_args()
        args = self.args[:]

        if args and ' ' in args[-1] and not args[-1].startswith(':'):
            args[-1] = f':{args[-1]}'

        return '{prefix}{command} {args}\r\n'.format(
            prefix=(f':{self.prefix} ' if self.prefix is not None else ''),
            command=str(self.command),
            args=' '.join(args),
        )

    def __repr__(self):
        return repr(str(self)[:-2])

    def __eq__(self, other):
        return (
            isinstance(other, Message)
            and self.prefix == other.prefix
            and self.command == other.command
            and self.args == other.args
        )
