#!/usr/bin/env python
from circuits.core.components import BaseComponent
from circuits.core.handlers import handler
from circuits.web import BaseServer, Controller
from circuits.web.dispatchers.dispatcher import Dispatcher

from .helpers import urljoin, urlopen


class PrefixingDispatcher(BaseComponent):
    """Forward to another Dispatcher based on the channel."""

    @handler("request", priority=1.0)
    def _on_request(self, event, request, response):
        path = request.path.strip("/")

        path = urljoin("/%s/" % self.channel, path)
        request.path = path


class DummyRoot(Controller):

    channel = "/"

    def index(self):
        return "Not used"


class Root1(Controller):

    channel = "/site1"

    def index(self):
        return "Hello from site 1!"


class Root2(Controller):

    channel = "/site2"

    def index(self):
        return "Hello from site 2!"


def test_disps(manager, watcher):
    server1 = BaseServer(0, channel="site1").register(manager)
    PrefixingDispatcher(channel="site1").register(manager)
    Dispatcher(channel="site1").register(manager)
    Root1().register(manager)
    assert watcher.wait("ready", channel=server1.channel)

    server2 = BaseServer(("localhost", 0), channel="site2").register(manager)
    PrefixingDispatcher(channel="site2").register(manager)
    Dispatcher(channel="site2").register(manager)
    Root2().register(manager)
    assert watcher.wait("ready", channel=server2.channel)

    DummyRoot().register(manager)

    f = urlopen(server1.http.base, timeout=3)
    s = f.read()
    assert s == b"Hello from site 1!"

    f = urlopen(server2.http.base, timeout=3)
    s = f.read()
    assert s == b"Hello from site 2!"
