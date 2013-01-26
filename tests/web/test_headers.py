#!/usr/bin/env python

from circuits.web import Controller

from .helpers import urlopen


class Root(Controller):

    def index(self):
        return "Hello World!"

    def foo(self):
        self.response.headers["Content-Type"] = "text/plain"
        return "Hello World!"


def test_default(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"

    content_type = f.headers["Content-Type"]
    assert content_type == "text/html"


def test_explicit(webapp):
    f = urlopen("{0:s}/foo".format(webapp.server.base))
    s = f.read()
    assert s == b"Hello World!"

    content_type = f.headers["Content-Type"]
    assert content_type == "text/plain"


def test_static(webapp):
    f = urlopen("{0:s}/static/test.css".format(webapp.server.base))
    s = f.read()
    assert s == b"body { }\n"

    content_type = f.headers["Content-Type"]
    assert content_type == "text/css"
