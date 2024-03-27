#!/usr/bin/env python
import json
from typing import NoReturn

from circuits.web import Controller
from circuits.web.exceptions import Forbidden, NotFound, Redirect

from .helpers import HTTPError, urlopen


class Root(Controller):
    def index(self) -> str:
        return 'Hello World!'

    def test_redirect(self) -> NoReturn:
        msg = '/'
        raise Redirect(msg)

    def test_forbidden(self) -> NoReturn:
        raise Forbidden

    def test_notfound(self) -> NoReturn:
        raise NotFound

    def test_contenttype(self) -> NoReturn:
        raise Exception

    def test_contenttype_json(self) -> NoReturn:
        self.response.headers['Content-Type'] = 'application/json'
        raise Exception

    def test_contenttype_json_no_debug(self) -> NoReturn:
        self.response.headers['Content-Type'] = 'application/json'
        self.request.print_debug = False
        raise Exception


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


def test_contenttype(webapp) -> None:
    try:
        urlopen('%s/test_contenttype' % webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 500
        assert e.msg == 'Internal Server Error'
        assert 'text/html' in e.headers.get('Content-Type')
    else:
        raise AssertionError


def test_contenttype_json(webapp) -> None:
    try:
        urlopen('%s/test_contenttype_json' % webapp.server.http.base)
    except HTTPError as e:
        assert 'json' in e.headers.get('Content-Type')
        result = json.loads(e.read().decode('utf-8'))
        assert result['code'] == 500
        assert result['name'] == 'Internal Server Error'
        assert result['description'] == ''
        assert 'raise Exception' in result['traceback']
    else:
        raise AssertionError


def test_contenttype_json_no_debug(webapp) -> None:
    try:
        urlopen('%s/test_contenttype_json_no_debug' % webapp.server.http.base)
    except HTTPError as e:
        assert 'json' in e.headers.get('Content-Type')
        result = json.loads(e.read().decode('utf-8'))
        assert result['code'] == 500
        assert result['name'] == 'Internal Server Error'
        assert result['description'] == ''
        assert 'traceback' not in result
    else:
        raise AssertionError
