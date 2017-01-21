#!/usr/bin/env python
from circuits import Component, Event
from circuits.web import Controller

from .helpers import urlopen


class hello(Event):

    """hello Event"""


class App(Component):

    def hello(self):
        return "Hello World!"


class Root(Controller):

    def index(self):
        return self.fire(hello())


def test(webapp):
    App().register(webapp)

    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"
