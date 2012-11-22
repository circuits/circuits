#!/usr/bin/env python

from circuits.web import Controller

from .helpers import urlencode, urlopen, HTTPError


class Root(Controller):

    def index(self):
        return "Hello World!"

    def test_args(self, *args, **kwargs):
        args = tuple((x.encode('utf-8') if type(x) != str else x for x in args))
        return "{0}\n{1}".format(repr(args), repr(kwargs))

    def test_redirect(self):
        return self.redirect("/")

    def test_forbidden(self):
        return self.forbidden()

    def test_notfound(self):
        return self.notfound()

    def test_failure(self):
        raise Exception()

def test_root(webapp):
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
    data = urlencode(kwargs).encode('utf-8')
    f = urlopen(url, data)
    data = f.read().decode('utf-8').split("\n")
    assert data[0] == repr(args)
    assert data[1] == repr(kwargs)

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

def test_failure(webapp):
    try:
        urlopen("%s/test_failure" % webapp.server.base)
    except HTTPError as e:
        assert e.code == 500
    else:
        assert False
