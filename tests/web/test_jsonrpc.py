#!/usr/bin/env python
from circuits import Component
from circuits.web import JSONRPC, Controller

from .helpers import urlopen
from .jsonrpclib import ServerProxy


class App(Component):

    def eval(self, s):
        return eval(s)


class Root(Controller):

    def index(self):
        return "Hello World!"


def test(webapp):
    rpc = JSONRPC("/rpc")
    test = App()
    rpc.register(webapp)
    test.register(webapp)

    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"

    url = "%s/rpc" % webapp.server.http.base
    jsonrpc = ServerProxy(url, allow_none=True, encoding='utf-8')

    data = jsonrpc.eval("1 + 2")
    assert data["result"] == 3

    rpc.unregister()
    test.unregister()
