"""Circuits Library - Web

circuits.web contains the circuits full stack web server that is HTTP
and WSGI compliant.
"""
from .controllers import BaseController, Controller, expose
from .dispatchers import XMLRPC, Dispatcher, Static, VirtualHosts
from .errors import forbidden, httperror, notfound, redirect
from .events import request, response, stream
from .loggers import Logger
from .servers import BaseServer, Server
from .sessions import Sessions
from .url import URL, parse_url

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
