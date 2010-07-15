#!/usr/bin/env python

from urllib2 import urlopen, HTTPError

from circuits.web import Controller

class Root(Controller):

    def index(self):
        pass

def test(webapp):
    try:
        urlopen(webapp.server.base)
    except HTTPError, e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False
