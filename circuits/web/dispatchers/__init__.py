# Package:  dispatchers
# Date:     26th February 2011
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Dispatchers

This package contains various circuits.web dispatchers
By default a ``circuits.web.Server`` Component uses the
``dispatcher.Dispatcher``
"""

from circuits.web.dispatchers.static import Static
from circuits.web.dispatchers.xmlrpc import XMLRPC
from circuits.web.dispatchers.websockets import WebSockets
from circuits.web.dispatchers.dispatcher import Dispatcher
from circuits.web.dispatchers.virtualhosts import VirtualHosts

try:
    from circuits.web.dispatchers.jsonrpc import JSONRPC
except ImportError:
    pass

try:
    from circuits.web.dispatchers.routes import Routes
except ImportError:
    pass

# hghooks: no-pyflakes
