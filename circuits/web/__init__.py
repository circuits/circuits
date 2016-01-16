"""Circuits Library - Web

circuits.web contains the circuits full stack web server that is HTTP
and WSGI compliant.
"""

from .loggers import Logger
from .sessions import Sessions
from .url import parse_url, URL
from .servers import BaseServer, Server
from .events import request, response, stream
from .controllers import expose, BaseController, Controller
from .errors import httperror, forbidden, notfound, redirect
from .dispatchers import Static, Dispatcher, VirtualHosts, XMLRPC

try:
    from .dispatchers import JSONRPC
except ImportError:
    pass

try:
    from .controllers import JSONController
except ImportError:
    pass

# flake8: noqa
# pylama: skip=1
