"""Dispatchers

This package contains various circuits.web dispatchers
By default a ``circuits.web.Server`` Component uses the
``dispatcher.Dispatcher``
"""
from ..websockets.dispatcher import WebSocketsDispatcher
from .dispatcher import Dispatcher
from .jsonrpc import JSONRPC
from .static import Static
from .virtualhosts import VirtualHosts
from .xmlrpc import XMLRPC

# flake8: noqa
# pylama: skip=1
