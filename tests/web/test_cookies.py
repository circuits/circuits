#!/usr/bin/env python
from circuits.web import Controller

from .helpers import CookieJar, HTTPCookieProcessor, build_opener


class Root(Controller):
    def index(self) -> str:
        visited = self.cookie.get('visited')
        if visited and visited.value:
            return 'Hello again!'
        self.cookie['visited'] = True
        return 'Hello World!'


def test(webapp) -> None:
    cj = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cj))

    f = opener.open(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'

    f = opener.open(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello again!'
