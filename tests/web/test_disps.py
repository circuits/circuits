#!/usr/bin/env python

from circuits.core.manager import Manager
from circuits.core.handlers import handler
from circuits.core.components import BaseComponent

from circuits.web import BaseServer, Controller
from circuits.web.dispatchers.dispatcher import Dispatcher

from .helpers import urlopen, urljoin


class PrefixingDispatcher(BaseComponent):

    """Forward to another Dispatcher based on the channel."""

    def __init__(self, channel):
        super(PrefixingDispatcher, self).__init__(channel=channel)

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


def test_disps():

    manager = Manager()

    server1 = BaseServer(0, channel="site1")
    server1.register(manager)
    PrefixingDispatcher(channel="site1").register(server1)
    Dispatcher(channel="site1").register(server1)
    Root1().register(manager)

    server2 = BaseServer(("localhost", 0), channel="site2")
    server2.register(manager)
    PrefixingDispatcher(channel="site2").register(server2)
    Dispatcher(channel="site2").register(server2)
    Root2().register(manager)

    DummyRoot().register(manager)
    manager.start()

    f = urlopen(server1.http.base, timeout=3)
    s = f.read()
    assert s == b"Hello from site 1!"

    f = urlopen(server2.http.base, timeout=3)
    s = f.read()
    assert s == b"Hello from site 2!"
