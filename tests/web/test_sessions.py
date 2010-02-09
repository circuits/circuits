#!/usr/bin/env python

import urllib2
from cookielib import CookieJar

from circuits.web import Server, Controller, Sessions

class Root(Controller):

    def index(self, name=None):
        if name:
            self.session["name"] = name
        else:
            name = self.session.get("name", "World!")

        return "Hello %s" % name

def test(app):
    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    f = opener.open(app.base + "/test_sessions")
    s = f.read() 
    assert s == "Hello World!"

    f = opener.open(app.base + "/test_sessions/test")
    assert f.read() == "Hello test"

    f = opener.open(app.base + "/test_sessions")
    assert f.read() == "Hello test"
