#!/usr/bin/env python
from circuits.web import Controller
from circuits.web.wsgi import Application

from .helpers import HTTPError, urlencode, urlopen


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
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"


def test_404(webapp):
    try:
        urlopen("%s/foo" % webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False


def test_args(webapp):
    args = ("1", "2", "3")
    kwargs = {"1": "one", "2": "two", "3": "three"}
    url = "%s/test_args/%s" % (webapp.server.http.base, "/".join(args))
    data = urlencode(kwargs).encode()

    f = urlopen(url, data)
    data = f.read().split(b"\n")
    assert eval(data[0]) == args
    assert eval(data[1]) == kwargs


def test_redirect(webapp):
    f = urlopen("%s/test_redirect" % webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"


def test_forbidden(webapp):
    try:
        urlopen("%s/test_forbidden" % webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 403
        assert e.msg == "Forbidden"
    else:
        assert False


def test_notfound(webapp):
    try:
        urlopen("%s/test_notfound" % webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False
