#!/usr/bin/env python
from circuits.web import Controller, expose

from .helpers import urlopen


class Root(Controller):

    @expose("test.txt")
    def index(self):
        return "Hello world!"


class Leaf(Controller):

    channel = "/test"

    @expose("test.txt")
    def index(self, vpath=None):
        if vpath is None:
            return "Hello world!"
        else:
            return "Hello world! " + vpath


def test(webapp):
    Leaf().register(webapp)

    f = urlopen(webapp.server.http.base + "/test.txt")
    s = f.read()
    assert s == b"Hello world!"

    f = urlopen(webapp.server.http.base + "/test/test.txt")
    s = f.read()
    assert s == b"Hello world!"
