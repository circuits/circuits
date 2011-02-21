# Module:   conftest
# Date:     10 February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""py.test config"""

import os
import errno
import socket

from circuits import Component
from circuits.web.wsgi import Gateway
from circuits.net.sockets import Close
from circuits.web import Server, Static

DOCROOT = os.path.join(os.path.dirname(__file__), "static")

class WebApp(Component):

    def __init__(self):
        super(WebApp, self).__init__()

        self.server = Server(0).register(self)

def pytest_funcarg__webapp(request):
    return request.cached_setup(
            setup=lambda: setupwebapp(request),
            teardown=lambda webapp: teardownwebapp(webapp),
            scope="module")

def setupwebapp(request):
    webapp = WebApp()

    if hasattr(request.module, "application"):
        application = getattr(request.module, "application")
        Gateway(application).register(webapp)
    else:
        Root = getattr(request.module, "Root", None)
        if Root:
            Root().register(webapp)

    Static("/static", DOCROOT, dirlisting=True).register(webapp)
    webapp.start()
    return webapp

def teardownwebapp(webapp):
    webapp.push(Close(), target=webapp.server)
    webapp.stop()
