# Module:   conftest
# Date:     10 February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""py.test config"""

import os

import pytest


DOCROOT = os.path.join(os.path.dirname(__file__), "static")


def pytest_funcarg__webapp(request):
    return request.cached_setup(
            setup=lambda: setupwebapp(request),
            teardown=lambda webapp: teardownwebapp(webapp),
            scope="module")


def setupwebapp(request):
    from circuits import Component

    class WebApp(Component):

        def __init__(self):
            super(WebApp, self).__init__()

            from circuits.web import Server

            self.server = Server(0).register(self)

    webapp = WebApp()

    if hasattr(request.module, "application"):
        from circuits.web.wsgi import Gateway
        application = getattr(request.module, "application")
        Gateway(application).register(webapp)
    else:
        Root = getattr(request.module, "Root", None)
        if Root:
            Root().register(webapp)

    from circuits.web import Static

    Static("/static", DOCROOT, dirlisting=True).register(webapp)
    waiter = pytest.WaitEvent(webapp, "ready")
    webapp.start()

    assert waiter.wait()

    return webapp


def teardownwebapp(webapp):
    from circuits.net.sockets import Close
    webapp.fire(Close(), webapp.server)
    webapp.stop()
