#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen

from circuits.web import expose, Controller

class Root(Controller):

    def index(self):
        return "Hello World!"

    @expose(u"你好")
    def hello(self):
        self.response.headers["Content-Type"] = "text/html; charset=utf-8"
        return u"世界您好"

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"

    url = u"%s/你好" % webapp.server.base
    f = urlopen(url.encode("utf-8"))
    s = f.read()
    s = s.decode("utf-8")
    assert s == u"世界您好"
