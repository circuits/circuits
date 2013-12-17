#!/usr/bin/env python

from circuits.web import Controller
from circuits import Component, Event

from .helpers import urlopen


class foo(Event):
    """foo Event"""


class App(Component):

    channel = "app"

    def foo(self):
        return "Hello World!"


class Root(Controller):

    def index(self):
        yield (yield self.call(foo(), "app"))


def test(webapp):
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"
