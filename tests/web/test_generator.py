#!/usr/bin/env python
from circuits.web import Controller

from .helpers import urlopen


class Root(Controller):
    def index(self):
        def response():
            yield 'Hello '
            yield 'World!'

        return response()


def test(webapp):
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'
