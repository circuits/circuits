#!/usr/bin/env python
from circuits.web import Controller, Sessions

from .helpers import CookieJar, HTTPCookieProcessor, build_opener


class Root(Controller):
    def index(self, vpath=None) -> str:
        if vpath:
            name = vpath
            with self.session as data:
                data['name'] = name
        else:
            name = self.session.get('name', 'World!')

        return 'Hello %s' % name

    def logout(self) -> str:
        self.session.expire()
        return 'OK'


def test(webapp) -> None:
    Sessions().register(webapp)

    cj = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cj))

    f = opener.open(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'

    f = opener.open(webapp.server.http.base + '/test')
    s = f.read()
    assert s == b'Hello test'

    f = opener.open(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello test'


def test_expire(webapp) -> None:
    Sessions().register(webapp)

    cj = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cj))

    f = opener.open(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'

    f = opener.open(webapp.server.http.base + '/test')
    s = f.read()
    assert s == b'Hello test'

    f = opener.open(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello test'

    f = opener.open(webapp.server.http.base + '/logout')
    s = f.read()
    assert s == b'OK'

    f = opener.open(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'
