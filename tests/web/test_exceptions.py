#!/usr/bin/env python

from urllib2 import urlopen, HTTPError

from circuits.web import Controller
from circuits.web.exceptions import *

class Root(Controller):

    def index(self):
        return "Hello World!"

    def test_redirect(self):
        raise Redirect("/")

    def test_forbidden(self):
        raise Forbidden()

    def test_notfound(self):
        raise NotFound()

def test_redirect(webapp):
    f = urlopen("%s/test_redirect" % webapp.server.base)
    s = f.read()
    assert s == "Hello World!"

def test_forbidden(webapp):
    try:
        urlopen("%s/test_forbidden" % webapp.server.base)
    except HTTPError, e:
        assert e.code == 403
        assert e.msg == "Forbidden"
    else:
        assert False

def test_notfound(webapp):
    try:
         urlopen("%s/test_notfound" % webapp.server.base)
    except HTTPError, e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False
