# Module:   conftest
# Date:     10 February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""py.test config"""

import os

import pytest

from circuits import Component
from circuits.net.sockets import Close
from circuits.web import Server, Static
from circuits.web.client import Client, Connect, Request


DOCROOT = os.path.join(os.path.dirname(__file__), "static")


class WebApp(Component):

    def init(self):
        self.server = Server(0).register(self)
        Static("/static", DOCROOT, dirlisting=True).register(self)


class WebClient(Client):

    def __call__(self, method, path, body=None, headers={}):
        waiter = pytest.WaitEvent(self, "response", channel=self.channel)
        self.fire(Request(method, path, body, headers))
        assert waiter.wait()

        return self.response


@pytest.fixture(scope="module")
def webapp(request):
    webapp = WebApp()

    if hasattr(request.module, "application"):
        from circuits.web.wsgi import Gateway
        application = getattr(request.module, "application")
        Gateway({"/": application}).register(webapp)

    Root = getattr(request.module, "Root", None)
    if Root is not None:
        Root().register(webapp)

    waiter = pytest.WaitEvent(webapp, "ready")
    webapp.start()
    assert waiter.wait()

    def finalizer():
        webapp.fire(Close(), webapp.server)
        webapp.stop()

    request.addfinalizer(finalizer)

    return webapp


@pytest.fixture(scope="module")
def webclient(request, webapp):
    webclient = WebClient(webapp.server.base)
    waiter = pytest.WaitEvent(webclient, "ready", channel=webclient.channel)
    webclient.register(webapp)
    assert waiter.wait()

    webclient.fire(Connect(), webclient)
    waiter = pytest.WaitEvent(
        webclient, "connected", channel=webclient.channel
    )
    assert waiter.wait()

    def finalizer():
        webclient.unregister()

    request.addfinalizer(finalizer)

    return webclient
