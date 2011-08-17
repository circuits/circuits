#!/usr/bin/env python

from circuits.web import Controller
from circuits import Event, Component

from .helpers import urlopen


class Hello(Event):
    """Hello Event"""

class Test(Component):

    def hello(self):
        return "Hello World!"

class Root(Controller):

    def index(self):
        return self.fire(Hello())

def test(webapp):
    Test().register(webapp)

    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"
