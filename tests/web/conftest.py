# Module:   conftest
# Date:     10 February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""py.test config"""

import os

from circuits import Component
from circuits.web.wsgi import Gateway
from circuits.web import Server, Static

BIND = ("127.0.0.1", 8000)
DOCROOT = os.path.join(os.path.dirname(__file__), "static")

class WebApp(Component):

    def __init__(self):
        super(WebApp, self).__init__()

        self.server = Server(BIND)
        self.server.register(self)

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
    webapp.stop()
