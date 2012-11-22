#!/usr/bin/env python

from urllib2 import urlopen

from circuits.web import expose, Controller


class Root(Controller):

    @expose("test.txt")
    def index(self):
        return "Hello world!"


class Leaf(Controller):

    channel = "/test"

    @expose("test.txt")
    def index(self, vpath=None):
        if vpath == None:
            return "Hello world!"
        else:
            return "Hello world! " + vpath


def test(webapp):
    Leaf().register(webapp)

    f = urlopen(webapp.server.base + "/test.txt")
    s = f.read()
    assert s == b"Hello world!"

    f = urlopen(webapp.server.base + "/test/test.txt")
    s = f.read()
    assert s == b"Hello world!"
