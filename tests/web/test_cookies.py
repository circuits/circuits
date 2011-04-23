#!/usr/bin/env python

try:
    from urllib.request import build_opener, HTTPCookieProcessor
except ImportError:
    from urllib2 import build_opener, HTTPCookieProcessor
try:
    from http.cookiejar import CookieJar
except ImportError:
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

def test(webapp):
    cj = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cj))

    f = opener.open(webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"

    f = opener.open(webapp.server.base)
    s = f.read()
    assert s == b"Hello again!"
