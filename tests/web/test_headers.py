#!/usr/bin/env python
from circuits.web import Controller

from .helpers import urlopen


class Root(Controller):
    def index(self) -> str:
        return 'Hello World!'

    def foo(self) -> str:
        self.response.headers['Content-Type'] = 'text/plain'
        return 'Hello World!'

    def empty(self) -> str:
        return ''


def test_default(webapp) -> None:
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'

    content_type = f.headers['Content-Type']
    assert content_type == 'text/html; charset=utf-8'


def test_explicit(webapp) -> None:
    f = urlopen(f'{webapp.server.http.base:s}/foo')
    s = f.read()
    assert s == b'Hello World!'

    content_type = f.headers['Content-Type']
    assert content_type == 'text/plain'


def test_static(webapp) -> None:
    f = urlopen(f'{webapp.server.http.base:s}/static/test.css')
    s = f.read()
    assert s == b'body { }\n'

    content_type = f.headers['Content-Type']
    assert content_type == 'text/css'


def test_empty(webapp) -> None:
    f = urlopen(f'{webapp.server.http.base:s}/empty')
    s = f.read()
    assert s == b''

    content_length = f.headers['Content-Length']
    assert int(content_length) == 0
