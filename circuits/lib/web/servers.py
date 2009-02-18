# Module:   server
# Date:     6th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Web Server

This module implements the Web Server Component.
"""

import os
from socket import gethostname as _gethostname

from circuits.core import listener, Component

from circuits.lib.sockets import TCPServer

from http import HTTP
from constants import SERVER_VERSION
from dispatchers import Dispatcher

class BaseServer(Component):

    def __init__(self, port, address="", **kwargs):
        self.server = TCPServer(port, address, **kwargs)
        self.http = HTTP(self, **kwargs)

        super(BaseServer, self).__init__(**kwargs)

        self.manager += self.server
        self.manager += self.http

        print "%s listening on %s" % (SERVER_VERSION, self.base())

    def registered(self):
        self.manager += self.server
        self.manager += self.http

    @property
    def address(self):
        return self.server.address

    @property
    def port(self):
        return self.server.port

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

    def poll(self):
        self.server.poll()

    def run(self):
        while True:
            try:
                self.flush()
                self.poll()
            except KeyboardInterrupt:
                break

class Server(BaseServer):

    def __init__(self, port, address="", docroot=None, **kwargs):
        super(Server, self).__init__(port, address, **kwargs)

        self.dispatcher = Dispatcher(**kwargs)
        self.manager += self.dispatcher

    def registered(self):
        super(Server, self).registered()

        self.manager += self.dispatcher

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
