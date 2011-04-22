#!/usr/bin/env python

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

from circuits.web import Controller

class Root(Controller):

    def index(self):
        yield "Hello "
        yield "World!"

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"
