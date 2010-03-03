#!/usr/bin/env python

from os.path import basename
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
    server = BaseServer(("0.0.0.0", 9000))
    BaseRoot().register(server)
    server.start()

    hostname = gethostname()
    assert server.host == "%s:9000" % hostname

    f = urlopen(server.base)
    s = f.read()
    assert s == "Hello World!"

def test_server():
    server = Server("0.0.0.0:9001")
    Root().register(server)
    server.start()

    hostname = gethostname()
    assert server.host == "%s:9001" % hostname

    f = urlopen(server.base)
    s = f.read()
    assert s == "Hello World!"

def test_unixserver(tmpdir):
    sockpath = tmpdir.ensure("test.sock")
    socket = str(sockpath)
    server = Server(socket)
    Root().register(server)
    server.start()

    assert basename(server.host) == "test.sock"

    server.stop()
