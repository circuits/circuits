#!/usr/bin/env python
from circuits.web import Controller

from .helpers import urlopen


class Root(Controller):
    def index(self, *args, **kwargs) -> str:
        return 'ERROR'


def application(environ, start_response):
    status = '200 OK'
    start_response(status, [])
    return ['']


def test(webapp) -> None:
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b''
    assert f.headers.get('Transfer-Encoding') != 'chunked'
