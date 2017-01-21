#!/usr/bin/env python
from .helpers import urlopen


def application(environ, start_response):
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    write = start_response(status, response_headers)
    write("Hello World!")
    return [""]


def test(webapp):
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"
