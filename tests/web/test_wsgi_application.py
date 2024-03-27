#!/usr/bin/env python
import json

import pytest

from circuits.web import Controller
from circuits.web.wsgi import Application

from .helpers import HTTPError, urlencode, urlopen


class Root(Controller):
    def index(self):
        return 'Hello World!'

    def test_args(self, *args, **kwargs):
        self.response.headers['Content-Type'] = 'application/json'
        return json.dumps(
            {
                'args': args,
                'kwargs': kwargs,
                'path': self.request.path,
                'uri_path': self.request.uri._path.decode(),
                'base_path': self.request.base._path.decode(),
                'method': self.request.method,
                'scheme': self.request.scheme,
                'protocol': self.request.protocol,
                'qs': self.request.qs,
                'script_name': self.request.script_name,
                'content_type': self.request.headers['Content-Type'],
            }
        )

    def test_redirect(self):
        return self.redirect('/')

    def test_forbidden(self):
        return self.forbidden()

    def test_notfound(self):
        return self.notfound()


application = Application() + Root()


def test(webapp):
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'


def test_404(webapp):
    with pytest.raises(HTTPError) as exc:
        urlopen('%s/foo' % webapp.server.http.base)
    assert exc.value.code == 404
    assert exc.value.msg == 'Not Found'


def test_args(webapp):
    args = ['1', '2', '3']
    kwargs = {'1': 'one', '2': 'two', '3': 'three'}
    url = '%s/test_args/%s' % (webapp.server.http.base, '/'.join(args))
    data = urlencode(kwargs).encode()

    f = urlopen(url, data)
    data = json.load(f)
    assert data['args'] == args
    assert data['kwargs'] == kwargs
    assert data['path'] == 'test_args/1/2/3'
    assert data['uri_path'] == '/test_args/1/2/3'
    assert data['base_path'] == '/'
    assert data['method'] == 'POST'
    assert data['scheme'] == 'http'
    assert data['protocol'] == [1, 1]
    assert data['qs'] == ''
    assert data['script_name'] == '/'
    assert data['content_type'] == 'application/x-www-form-urlencoded'


def test_redirect(webapp):
    f = urlopen('%s/test_redirect' % webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'


def test_forbidden(webapp):
    with pytest.raises(HTTPError) as exc:
        urlopen('%s/test_forbidden' % webapp.server.http.base)
    assert exc.value.code == 403
    assert exc.value.msg == 'Forbidden'


def test_notfound(webapp):
    with pytest.raises(HTTPError) as exc:
        urlopen('%s/test_notfound' % webapp.server.http.base)
    assert exc.value.code == 404
    assert exc.value.msg == 'Not Found'
