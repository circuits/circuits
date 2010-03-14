#!/usr/bin/env python

from urllib2 import urlopen

import jsonrpclib

from circuits import Component
from circuits.web import Controller, JSONRPC

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
    assert s == "Hello World!"

    url = "%s/rpc/" % webapp.server.base
    jsonrpc = jsonrpclib.ServerProxy(url, allow_none=True)

    data = jsonrpc.eval("1 + 2")
    assert data["result"] == 3

    rpc.unregister()
    test.unregister()
