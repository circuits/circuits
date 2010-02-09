#!/usr/bin/env python

from urllib2 import urlopen

from circuits.web import Server, Controller, Sessions

class Root(Controller):

    def index(self):
        yield "Hello "
        yield "World!"

def test(app):
    f = urlopen(app.base)
    assert f.read() == "Hello World!"
