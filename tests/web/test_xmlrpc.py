#!/usr/bin/env python
from xmlrpc.client import ServerProxy

from circuits import Component
from circuits.web import XMLRPC, Controller

from .helpers import urlopen


class App(Component):

    async def eval(self, s):
        return eval(s)


class Root(Controller):

    async def index(self):
        return "Hello World!"


def test(webapp):
    rpc = XMLRPC("/rpc")
    test = App()
    rpc.register(webapp)
    test.register(webapp)

    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"

    url = "%s/rpc" % webapp.server.http.base
    server = ServerProxy(url, allow_none=True)

    r = server.eval("1 + 2")
    assert r == 3

    rpc.unregister()
    test.unregister()
