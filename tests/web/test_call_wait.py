#!/usr/bin/env python
from circuits import Component, Event
from circuits.web import Controller

from .helpers import urlopen


class foo(Event):

    """foo Event"""


class App(Component):

    channel = "app"

    def foo(self):
        return "Hello World!"


class Root(Controller):

    def index(self):
        value = (yield self.call(foo(), "app"))
        yield value.value


def test(webapp):
    app = App().register(webapp)
    try:
        f = urlopen(webapp.server.http.base)
        s = f.read()
        assert s == b"Hello World!"
    finally:
        app.unregister()
