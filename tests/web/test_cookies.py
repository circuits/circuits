#!/usr/bin/env python

import urllib.request, urllib.error, urllib.parse
from http.cookiejar import CookieJar
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
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    f = opener.open(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"

    f = opener.open(webapp.server.base)
    s = f.read()
    assert s == "Hello again!"
