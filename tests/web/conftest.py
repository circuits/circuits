"""py.test config"""
import os

import pytest

from circuits import Component, Debugger, handler
from circuits.net.sockets import close
from circuits.web import Server, Static
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


@pytest.fixture
def webapp(request, manager, watcher):
    webapp = WebApp().register(manager)
    assert watcher.wait("ready")

    if hasattr(request.module, "application"):
        from circuits.web.wsgi import Gateway
        application = getattr(request.module, "application")
        Gateway({"/": application}).register(webapp)
        assert watcher.wait("registered")

    Root = getattr(request.module, "Root", None)
    if Root is not None:
        Root().register(webapp)
        assert watcher.wait("registered")

    if request.config.option.verbose:
        Debugger().register(webapp)
        assert watcher.wait("registered")

    def finalizer():
        webapp.fire(close())
        assert watcher.wait("closed")

        webapp.unregister()
        assert watcher.wait("unregistered")

    request.addfinalizer(finalizer)

    return webapp
