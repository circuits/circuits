#!/usr/bin/env python

from urllib2 import urlopen

from circuits.web.wsgi import Gateway

def application(environ, start_response):
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    start_response(status, response_headers)
    return "Hello World!"

def fooApp(environ, start_response):
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    start_response(status, response_headers)
    return "Foo"

def test(webapp):
    foo = Gateway(fooApp, "/foo")
    foo.register(webapp)

    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"

    f = urlopen("%s/foo" % webapp.server.base)
    s = f.read()
    assert s == "Foo"

    foo.unregister()
