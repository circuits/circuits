#!/usr/bin/env python

from urllib2 import urlopen, HTTPError

from circuits import Component

class Root(Component):

    channel = "web"

    def request(self, request, response):
        raise Exception()

def test(webapp):
    try:
        f = urlopen(webapp.server.base)
    except HTTPError, e:
        assert e.code == 500
    else:
        assert False
