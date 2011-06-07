#!/usr/bin/env python

import pytest

try:
    from urllib.parse import urlencode
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen
    from urllib2 import HTTPError

from circuits.web import Controller
from circuits.web.wsgi import Application

from .helpers import urlencode, urlopen, HTTPError


class Root(Controller):

    def index(self):
        return "Hello World!"

    def test_args(self, *args, **kwargs):
        args = [arg if isinstance(arg, str) else arg.encode() for arg in args]
        return "%s\n%s" % (repr(tuple(args)), repr(kwargs))

    def test_redirect(self):
        return self.redirect("/")

    def test_forbidden(self):
        return self.forbidden()

    def test_notfound(self):
        return self.notfound()

application = Application() + Root()

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"

def test_404(webapp):
    try:
        urlopen("%s/foo" % webapp.server.base)
    except HTTPError as e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False

def test_args(webapp):
    args = ("1", "2", "3")
    kwargs = {"1": "one", "2": "two", "3": "three"}
    url = "%s/test_args/%s" % (webapp.server.base, "/".join(args))
    data = urlencode(kwargs).encode()

    f = urlopen(url, data)
    data = f.read().split(b"\n")
    assert data[0] == repr(args).encode()
    assert data[1] == repr(kwargs).encode()

def test_redirect(webapp):
    f = urlopen("%s/test_redirect" % webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"

def test_forbidden(webapp):
    try:
        urlopen("%s/test_forbidden" % webapp.server.base)
    except HTTPError as e:
        assert e.code == 403
        assert e.msg == "Forbidden"
    else:
        assert False

def test_notfound(webapp):
    try:
         urlopen("%s/test_notfound" % webapp.server.base)
    except HTTPError as e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False
