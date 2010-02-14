#!/usr/bin/env python

from urllib2 import urlopen, HTTPError

from circuits.web import Controller, Static

class Root(Controller):

    def index(self):
        return "Hello World!"

def test(webapp):
    if not Static in webapp:
        Static("/static", "static", dirlisting=True).register(webapp)

    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"

def test_404(webapp):
    if not Static in webapp:
        Static("/static", "static", dirlisting=True).register(webapp)

    try:
        urlopen("%s/foo" % webapp.server.base)
    except HTTPError, e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False

def test_file(webapp):
    if not Static in webapp:
        Static("/static", "static", dirlisting=True).register(webapp)

    url = "%s/static/helloworld.txt" % webapp.server.base
    f = urlopen(url)
    s = f.read().strip()
    assert s == "Hello World!"

def test_file404(webapp):
    if not Static in webapp:
        Static("/static", "static", dirlisting=True).register(webapp)

    try:
        urlopen("%s/static/foo.txt" % webapp.server.base)
    except HTTPError, e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False

def test_directory(webapp):
    if not Static in webapp:
        Static("/static", "static", dirlisting=True).register(webapp)

    f = urlopen("%s/static/" % webapp.server.base)
    s = f.read()
    assert "helloworld.txt" in s
