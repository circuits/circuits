"""Internet Relay Chat Protocol

This package implements the Internet Relay Chat Protocol
or commonly known as IRC. Support for both server and client
is implemented.
"""


from .commands import *
from .numerics import *
from .protocol import IRC
from .message import Message
from .events import response, reply
from .utils import joinprefix, parsemsg, parseprefix, strip


sourceJoin = joinprefix
sourceSplit = parseprefix


# pylama:skip=1
