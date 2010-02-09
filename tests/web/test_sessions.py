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

app = Server(8000) + Sessions() + Root()

def test():
    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    f = opener.open("http://localhost:8000/test_sessions")
    assert f.read() == "Hello World!"

    f = opener.open("http://localhost:8000/test_sessions/test")
    assert f.read() == "Hello test"

    f = opener.open("http://localhost:8000/test_sessions")
    assert f.read() == "Hello test"

def pytest_session_finish():
    app.stop()
