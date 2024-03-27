#!/usr/bin/env python
from circuits.web import Controller, expose

from .helpers import urlopen


class Root(Controller):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self += Hello()
        self += World()

    def index(self) -> str:
        return 'index'

    def hello1(self) -> str:
        return 'hello1'

    @expose('hello2')
    def hello2(self) -> str:
        return 'hello2'

    def query(self, test) -> str:
        return 'query %s' % test


class Hello(Controller):
    channel = '/hello'

    def index(self) -> str:
        return 'hello index'

    def test(self) -> str:
        return 'hello test'

    def query(self, test) -> str:
        return 'hello query %s' % test


class World(Controller):
    channel = '/world'

    def index(self) -> str:
        return 'world index'

    def test(self) -> str:
        return 'world test'


def test_simple(webapp) -> None:
    url = '%s/hello1' % webapp.server.http.base
    f = urlopen(url)
    s = f.read()
    assert s == b'hello1'


def test_expose(webapp) -> None:
    url = '%s/hello2' % webapp.server.http.base
    f = urlopen(url)
    s = f.read()
    assert s == b'hello2'


def test_index(webapp) -> None:
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b'index'


def test_controller_index(webapp) -> None:
    url = '%s/hello/' % webapp.server.http.base
    f = urlopen(url)
    s = f.read()
    assert s == b'hello index'

    url = '%s/world/' % webapp.server.http.base
    f = urlopen(url)
    s = f.read()
    assert s == b'world index'


def test_controller_expose(webapp) -> None:
    url = '%s/hello/test' % webapp.server.http.base
    f = urlopen(url)
    s = f.read()
    assert s == b'hello test'

    url = '%s/world/test' % webapp.server.http.base
    f = urlopen(url)
    s = f.read()
    assert s == b'world test'


def test_query(webapp) -> None:
    url = '%s/query?test=1' % webapp.server.http.base
    f = urlopen(url)
    s = f.read()
    assert s == b'query 1'

    url = '%s/hello/query?test=2' % webapp.server.http.base
    f = urlopen(url)
    s = f.read()
    assert s == b'hello query 2'
