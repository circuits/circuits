#!/usr/bin/env python
from typing import NoReturn

import pytest

from circuits.web import Controller

from .helpers import HTTPError, urlencode, urlopen


class Root(Controller):
    def index(self) -> str:
        return 'Hello World!'

    def test_args(self, *args, **kwargs) -> str:
        return f'{args!r}\n{kwargs!r}'

    def test_default_args(self, a=None, b=None) -> str:
        return f'a={a}\nb={b}'

    def test_redirect(self):
        return self.redirect('/')

    def test_forbidden(self):
        return self.forbidden()

    def test_notfound(self):
        return self.notfound()

    def test_failure(self) -> NoReturn:
        raise Exception


def test_root(webapp) -> None:
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'


def test_404(webapp) -> None:
    try:
        urlopen('%s/foo' % webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 404
        assert e.msg == 'Not Found'
    else:
        raise AssertionError


def test_args(webapp) -> None:
    args = ('1', '2', '3')
    kwargs = {'1': 'one', '2': 'two', '3': 'three'}
    url = '{}/test_args/{}'.format(webapp.server.http.base, '/'.join(args))
    data = urlencode(kwargs).encode('utf-8')
    f = urlopen(url, data)
    data = f.read().split(b'\n')
    assert eval(data[0]) == args
    assert eval(data[1]) == kwargs


@pytest.mark.parametrize(
    'data,expected',
    [
        ((['1'], {}), b'a=1\nb=None'),
        ((['1', '2'], {}), b'a=1\nb=2'),
        ((['1'], {'b': '2'}), b'a=1\nb=2'),
    ],
)
def test_default_args(webapp, data, expected) -> None:
    args, kwargs = data
    url = '{:s}/test_default_args/{:s}'.format(
        webapp.server.http.base,
        '/'.join(args),
    )
    data = urlencode(kwargs).encode('utf-8')
    f = urlopen(url, data)
    assert f.read() == expected


def test_redirect(webapp) -> None:
    f = urlopen('%s/test_redirect' % webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'


def test_forbidden(webapp) -> None:
    try:
        urlopen('%s/test_forbidden' % webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 403
        assert e.msg == 'Forbidden'
    else:
        raise AssertionError


def test_notfound(webapp) -> None:
    try:
        urlopen('%s/test_notfound' % webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 404
        assert e.msg == 'Not Found'
    else:
        raise AssertionError


def test_failure(webapp) -> None:
    try:
        urlopen('%s/test_failure' % webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 500
    else:
        raise AssertionError
