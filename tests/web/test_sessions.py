#!/usr/bin/env python

import urllib2
from cookielib import CookieJar

from circuits.web import Controller, Sessions

class Root(Controller):

    def index(self, name=None):
        if name:
            self.session["name"] = name
        else:
            name = self.session.get("name", "World!")

        return "Hello %s" % name

def test(webapp):
    Sessions().register(webapp)

    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    f = opener.open(webapp.server.base)
    s = f.read() 
    assert s == "Hello World!"

    f = opener.open(webapp.server.base + "/test")
    s = f.read()
    assert s == "Hello test"

    f = opener.open(webapp.server.base)
    s = f.read()
    assert s == "Hello test"
