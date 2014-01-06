# Module:   __init__
# Date:     3rd October 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Circuits Library - Web

circuits.web contains the circuits full stack web server that is HTTP
and WSGI compliant.
"""

from .loggers import Logger
from .sessions import Sessions
from .url import parse_url, URL
from .servers import BaseServer, Server
from .controllers import expose, Controller
from .events import request, response, stream
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

from .version import version as __version__

# flake8: noqa

# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
