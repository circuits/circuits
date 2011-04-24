#!/usr/bin/env python

from circuits.web.wsgi import Gateway

from .helpers import urlopen


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
    assert s == b"Hello World!"

    f = urlopen("%s/foo" % webapp.server.base)
    s = f.read()
    assert s == b"Foo"

    foo.unregister()
