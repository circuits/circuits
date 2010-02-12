#!/usr/bin/env python

from urllib2 import urlopen
from rfc822 import parsedate
from time import gmtime, mktime

from circuits.web import Controller

class Root(Controller):

    def index(self):
        self.expires(60)
        return "Hello World!"

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s  == "Hello World!"
    expires = f.headers["Expires"]
    diff = (mktime(parsedate(expires)) - mktime(gmtime()))
    assert 59.9 < diff < 60.1
