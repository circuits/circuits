#!/usr/bin/env python

from circuits.web import Controller
from circuits.web.exceptions import Forbidden, NotFound, Redirect

from .helpers import urlopen, HTTPError


class Root(Controller):

    def index(self):
        return "Hello World!"

    def test_redirect(self):
        raise Redirect("/")

    def test_forbidden(self):
        raise Forbidden()

    def test_notfound(self):
        raise NotFound()

    def test_contenttype(self):
        self.response.headers["Content-Type"] = "application/json"
        raise Exception()


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


def test_contenttype(webapp):
    try:
        f = urlopen("%s/test_contenttype" % webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 500
        assert e.msg == "Internal Server Error"
        assert e.headers.get("Content-Type") == "text/html"
    else:
        assert False
