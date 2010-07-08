#!/usr/bin/env python

from urllib import urlencode
from urllib2 import urlopen, HTTPError

from circuits.web import Controller
from circuits.web.wsgi import Application

class Root(Controller):

    def index(self):
        return "Hello World!"

    def test_args(self, *args, **kwargs):
        return "%s\n%s" % (repr(args), repr(kwargs))

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
    assert s == "Hello World!"

def test_404(webapp):
    try:
        urlopen("%s/foo" % webapp.server.base)
    except HTTPError, e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False

def test_args(webapp):
    args = (u"1", u"2", u"3")
    kwargs = {"1": "one", "2": "two", "3": "three"}
    url = "%s/test_args/%s" % (webapp.server.base, "/".join(args))
    data = urlencode(kwargs)

    f = urlopen(url, data)
    data = f.read().split("\n")
    assert data[0] == repr(args)
    assert data[1] == repr(kwargs)

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
