#!/usr/bin/env python

import xmlrpclib
from urllib2 import urlopen

from circuits import Component
from circuits.web import Controller, XMLRPC

class Test(Component):

    def eval(self, s):
        return eval(s)

class Root(Controller):

    def index(self):
        return "Hello World!"

def test(webapp):
    rpc = XMLRPC("/rpc")
    test = Test()
    rpc.register(webapp)
    test.register(webapp)

    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"

    url = "%s/rpc/" % webapp.server.base
    xmlrpc = xmlrpclib.ServerProxy(url, allow_none=True)

    r = xmlrpc.eval("1 + 2")
    assert r == 3

    rpc.unregister()
    test.unregister()
