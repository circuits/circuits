#!/usr/bin/env python

from urllib2 import urlopen

from circuits.web import Server, Controller, Sessions

class Root(Controller):

    def index(self):
        yield "Hello "
        yield "World!"

app = Server(8000) + Sessions() + Root()

def test():
    f = urlopen("http://localhost:8000/test_generators")
    assert f.read() == "Hello World!"

def pytest_session_finish():
    app.stop()
