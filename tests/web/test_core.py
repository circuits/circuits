#!/usr/bin/env python

from urllib2 import urlopen
from urllib import urlencode

from circuits.web import Server, Controller, Sessions

class Root(Controller):

    def index(self):
        return "Hello World!"

    def test_args(self, *args, **kwargs):
        return "%s\n%s" % (repr(args), repr(kwargs))

    def test_redirect(self):
        return self.redirect("/")

app = Server(8000) + Sessions() + Root()

def test():
    f = urlopen("http://localhost:8000/")
    assert f.read() == "Hello World!"

def test_args():
    args = ("1", "2", "3")
    kwargs = {"1": "one", "2": "two", "3": "three"}
    url = "http://localhost:8000/test_args/%s" % "/".join(args)
    data = urlencode(kwargs)

    f = urlopen(url, data)
    data = f.read().split("\n")
    assert data[0] == repr(args)
    assert data[1] == repr(kwargs)

def test_redirect():
    f = urlopen("http://localhost:8000/test_redirect")
    assert f.read() == "Hello World!"

def pytest_session_finish():
    app.stop()
