"""Internet Relay Chat Protocol

This package implements the Internet Relay Chat Protocol
or commonly known as IRC. Support for both server and client
is implemented.
"""
from .commands import *  # noqa
from .events import reply, response  # noqa
from .message import Message  # noqa
from .numerics import *  # noqa
from .protocol import IRC  # noqa
from .utils import joinprefix, parsemsg, parseprefix, strip  # noqa

sourceJoin = joinprefix
sourceSplit = parseprefix

# pylama:skip=1
