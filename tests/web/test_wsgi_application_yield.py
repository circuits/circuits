#!/usr/bin/env python

from urllib2 import urlopen

from circuits.web import Controller
from circuits.web.wsgi import Application

class Root(Controller):

    def index(self):
        yield "Hello "
        yield "World!"

application = Application() + Root()

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"
