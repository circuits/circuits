# Module:   conftest
# Date:     10 February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""py.test config"""

import os

import pytest

from circuits.net.sockets import close
from circuits.web import Server, Static
from circuits import handler, Component, Debugger
from circuits.web.client import Client, request


DOCROOT = os.path.join(os.path.dirname(__file__), "static")


class WebApp(Component):

    channel = "web"

    def init(self):
        self.closed = False

        self.server = Server(0).register(self)
        Static("/static", DOCROOT, dirlisting=True).register(self)


class WebClient(Client):

    def init(self, *args, **kwargs):
        self.closed = False

    def __call__(self, method, path, body=None, headers={}):
        waiter = pytest.WaitEvent(self, "response", channel=self.channel)
        self.fire(request(method, path, body, headers))
        assert waiter.wait()

        return self.response

    @handler("closed", channel="*", priority=1.0)
    def _on_closed(self):
        self.closed = True


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

    if request.config.option.verbose:
        Debugger().register(webapp)

    waiter = pytest.WaitEvent(webapp, "ready")
    webapp.start()
    assert waiter.wait()

    def finalizer():
        webapp.fire(close(), webapp.server)
        webapp.stop()

    request.addfinalizer(finalizer)

    return webapp


@pytest.fixture(scope="module")
def webclient(request, webapp):
    webclient = WebClient()
    waiter = pytest.WaitEvent(webclient, "ready", channel=webclient.channel)
    webclient.register(webapp)
    assert waiter.wait()

    def finalizer():
        webclient.unregister()

    request.addfinalizer(finalizer)

    return webclient
