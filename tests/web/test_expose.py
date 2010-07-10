#!/usr/bin/env python

from urllib2 import urlopen, HTTPError

from circuits.web import expose, Controller

class Root(Controller):

    def index(self):
        return "Hello World!"

    @expose("+test")
    def test(self):
        return "test"

    @expose("foo+bar", "foo_bar")
    def foobar(self):
        return "foobar"

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"

    f = urlopen("%s/+test" % webapp.server.base)
    s = f.read()
    assert s == "test"

    f = urlopen("%s/foo+bar" % webapp.server.base)
    s = f.read()
    assert s == "foobar"

    f = urlopen("%s/foo_bar" % webapp.server.base)
    s = f.read()
    assert s == "foobar"
