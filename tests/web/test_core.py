#!/usr/bin/env python
import pytest

from circuits.six import b, u
from circuits.web import Controller

from .helpers import HTTPError, urlencode, urlopen


class Root(Controller):

    def index(self):
        return "Hello World!"

    def test_args(self, *args, **kwargs):
        return "{0}\n{1}".format(repr(args), repr(kwargs))

    def test_default_args(self, a=None, b=None):
        return "a={0}\nb={1}".format(a, b)

    def test_redirect(self):
        return self.redirect("/")

    def test_forbidden(self):
        return self.forbidden()

    def test_notfound(self):
        return self.notfound()

    def test_failure(self):
        raise Exception()


def test_root(webapp):
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
    data = urlencode(kwargs).encode('utf-8')
    f = urlopen(url, data)
    data = f.read().split(b"\n")
    assert eval(data[0]) == args
    assert eval(data[1]) == kwargs


@pytest.mark.parametrize("data,expected", [
    ((["1"], {}), b("a=1\nb=None")),
    ((["1", "2"], {}), b("a=1\nb=2")),
    ((["1"], {"b": "2"}), b("a=1\nb=2")),
])
def test_default_args(webapp, data, expected):
    args, kwargs = data
    url = u("{0:s}/test_default_args/{1:s}".format(
        webapp.server.http.base,
        u("/").join(args)
    ))
    data = urlencode(kwargs).encode("utf-8")
    f = urlopen(url, data)
    assert f.read() == expected


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


def test_failure(webapp):
    try:
        urlopen("%s/test_failure" % webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 500
    else:
        assert False
