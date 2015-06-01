"""Dispatchers

This package contains various circuits.web dispatchers
By default a ``circuits.web.Server`` Component uses the
``dispatcher.Dispatcher``
"""

from .static import Static
from .xmlrpc import XMLRPC
from .jsonrpc import JSONRPC
from .dispatcher import Dispatcher
from .virtualhosts import VirtualHosts
from ..websockets.dispatcher import WebSocketsDispatcher

# flake8: noqa
# pylama: skip=1
