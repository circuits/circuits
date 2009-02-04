# Module:   server
# Date:     6th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Web Server

This module implements the Web Server Component.
"""

from socket import gethostname

from circuits.core import listener, Component

from circuits.lib.sockets import TCPServer

from http import HTTP
from constants import SERVER_VERSION
from dispatchers import DefaultDispatcher

class BaseServer(Component):

    def __init__(self, port, address="", **kwargs):
        super(BaseServer, self).__init__(**kwargs)

        self.server = TCPServer(port, address)
        self.http = HTTP()

        self.manager += self.server
        self.manager += self.http

        if self.server.address in ["", "0.0.0.0"]:
            bound = "%s:%s" % (gethostname(), self.server.port)
        else:
            bound = "%s:%s" % (self.address, self.server.port)

        print "%s listening on http://%s/" % (SERVER_VERSION, bound)

    def registered(self):
        self.manager += self.server
        self.manager += self.http

    def run(self):
        while True:
            try:
                self.flush()
                self.server.poll()
            except KeyboardInterrupt:
                break

class Server(BaseServer):

    def __init__(self, port, address="", docroot=None, **kwargs):
        super(Server, self).__init__(port, address, **kwargs)

        self.dispatcher = DefaultDispatcher()
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
