#!/usr/bin/env python

from circuits.web import Controller

from .helpers import urlopen


class Root(Controller):

    def index(self):
        print 'INDEX'
        def response():
            yield "Hello "
            yield "World!"
        return response()

def test(webapp):
    from circuits import Debugger
    Debugger().register(webapp)
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"
