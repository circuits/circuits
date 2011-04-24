#!/usr/bin/env python

from circuits.web import Controller

from .helpers import urlopen


class Root(Controller):

    def index(self):
        yield "Hello "
        yield "World!"

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"
