# Module:   server
# Date:     6th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Web Server

This module implements the Web Server Component.
"""

import os
from socket import gethostname as _gethostname

from circuits import Component

from circuits.lib.sockets import TCPServer

from http import HTTP
from webob import Request, Host
from constants import SERVER_VERSION
from dispatchers import Dispatcher

class BaseServer(Component):

    channel = "web"

    def __init__(self, port, address="", docroot=None, channel=channel):
        super(BaseServer, self).__init__(channel=channel)

        self.server = TCPServer(port, address, channel=channel)
        HTTP(self, channel=channel).register(self.server)

        Request.server = self
        Request.local = Host(self.server.address, self.server.port)

        self.server.register(self)

        print "%s listening on %s" % (SERVER_VERSION, self.base())

    @property
    def address(self):
        if hasattr(self, "server"):
            return self.server.address
        else:
            return None

    @property
    def port(self):
        if hasattr(self, "server"):
            return self.server.port
        return None

    def base(self):
        host = self.server.address
        if host in ("0.0.0.0", "::", ""):
            # 0.0.0.0 is INADDR_ANY and :: is IN6ADDR_ANY.
            # Look up the host name, which should be the
            # safest thing to spit out in a URL.
            host = _gethostname()
        
        port = self.server.port
        
        if self.server.ssl:
            scheme = "https"
            if port != 443:
                host += ":%s" % port
        else:
            scheme = "http"
            if port != 80:
                host += ":%s" % port
        
        return "%s://%s" % (scheme, host)


class Server(BaseServer):

    def __init__(self, port, address="", docroot=None, **kwargs):
        super(Server, self).__init__(port, address, docroot, **kwargs)

        self.dispatcher = Dispatcher(docroot=docroot, **kwargs)
        self += self.dispatcher

    def _getDocRoot(self):
        if hasattr(self, "dispatcher"):
            return self.dispatcher.docroot
        else:
            return None

    def _setDocRoot(self, docroot):
        if os.path.exists(docroot):
            self.dispatcher.docroot = docroot
        else:
            raise IOError(2, "Invalid docroot path", docroot)

    docroot = property(_getDocRoot, _setDocRoot, "Document Root")
