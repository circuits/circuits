#!/usr/bin/env python

import urllib2
from cookielib import CookieJar

from circuits.web import Server, Controller

class Root(Controller):

    def index(self):
        visited = self.cookie.get("visited")
        if visited and visited.value:
            return "Hello again!"
        else:
            self.cookie["visited"] = True
            return "Hello World!"

app = Server(8000) + Root()

def test():
    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    f = opener.open("http://localhost:8000/")
    assert f.read() == "Hello World!"

    f = opener.open("http://localhost:8000/")
    assert f.read() == "Hello again!"

def pytest_session_finish():
    app.stop()
