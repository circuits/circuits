#!/usr/bin/env python

from urllib2 import urlopen
from socket import gethostname

from circuits import Component
from circuits.web import Controller
from circuits.web import BaseServer, Server

class BaseRoot(Component):

    channel = "web"

    def request(self, request, response):
        return "Hello World!"

class Root(Controller):

    def index(self):
        return "Hello World!"

def test_baseserver():
    server = BaseServer(("0.0.0.0", 8000))
    BaseRoot().register(server)
    server.start()

    hostname = gethostname()
    assert server.host == "%s:8000" % hostname

    f = urlopen(server.base)
    s = f.read()
    assert s == "Hello World!"

    server.stop()

def test_server():
    server = Server(("0.0.0.0", 8001))
    Root().register(server)
    server.start()

    hostname = gethostname()
    assert server.host == "%s:8001" % hostname

    f = urlopen(server.base)
    s = f.read()
    assert s == "Hello World!"

    server.stop()
