#!/usr/bin/env python

from circuits.web.wsgi import Gateway

from .helpers import urlopen


def application(environ, start_response):
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    start_response(status, response_headers)
    return "Hello World!"


def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"
