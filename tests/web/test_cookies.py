#!/usr/bin/env python

import py
import urllib2
from cookielib import CookieJar
from circuits.web import Controller

class Root(Controller):
    def index(self):
        visited = self.cookie.get("visited")
        if visited and visited.value:
            return "Hello again!"
        else:
            self.cookie["visited"] = True
            return "Hello World!"

def test(app):
    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    f = opener.open(app.base)
    assert f.read() == "Hello World!"

    f = opener.open(app.base)
    assert f.read() == "Hello again!"
