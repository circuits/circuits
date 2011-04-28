#!/usr/bin/env python

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

from circuits import Component
from circuits.web import Controller, JSONRPC

from .jsonrpclib import ServerProxy
from .helpers import urlopen

class Test(Component):

    def eval(self, s):
        return eval(s)

class Root(Controller):

    def index(self):
        return "Hello World!"

def test(webapp):
    rpc = JSONRPC("/rpc")
    test = Test()
    rpc.register(webapp)
    test.register(webapp)

    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"

    url = "%s/rpc/" % webapp.server.base
    jsonrpc = ServerProxy(url, allow_none=True, encoding='utf-8')

    data = jsonrpc.eval("1 + 2")
    assert data["result"] == 3

    rpc.unregister()
    test.unregister()
