#!/usr/bin/env python
# -*- coding: utf-8 -*-

from circuits.web import expose, Controller

from .helpers import urlopen


class Root(Controller):

    def index(self):
        return "Hello World!"

    @expose("hello")
    def hello(self):
        self.response.headers["Content-Type"] = "text/html; charset=utf-8"
        return "Hello World!"

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"

    url = "%s/hello" % webapp.server.base
    f = urlopen(url)
    s = f.read()
    assert s == b"Hello World!"
