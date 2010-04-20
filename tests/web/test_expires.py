#!/usr/bin/env python

from urllib2 import urlopen
from rfc822 import parsedate
from datetime import datetime
from time import gmtime, mktime

from circuits.web import Controller

class Root(Controller):

    def index(self):
        self.expires(60)
        return "Hello World!"

    def nocache(self):
        self.expires(0)
        return "Hello World!"

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s  == "Hello World!"
    expires = f.headers["Expires"]
    diff = (mktime(parsedate(expires)) - mktime(gmtime()))
    assert 60 - (60 * 0.1) < diff < 60 + (60 * 0.1) # diff is about 60 +- 10%

def test_nocache(webapp):
    f = urlopen("%s/nocache" % webapp.server.base)
    s = f.read()
    assert s  == "Hello World!"

    expires = f.headers["Expires"]
    pragma = f.headers["Pragma"]
    cacheControl = f.headers["Cache-Control"]

    now = datetime.utcnow()
    lastyear = now.replace(year=now.year-1)

    diff = (mktime(parsedate(expires)) - mktime(lastyear.utctimetuple()))
    assert diff < 1.0

    assert pragma == "no-cache"
    assert cacheControl == "no-cache, must-revalidate"
