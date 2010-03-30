#!/usr/bin/env python

from urllib2 import urlopen, HTTPError

def application(environ, start_response):
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    start_response(status, response_headers)
    raise Exception("Hello World!")

def test(webapp):
    try:
        urlopen(webapp.server.base)
    except HTTPError, e:
        assert e.code == 500
        assert e.msg == "Internal Server Error"
        s = e.read()
        assert "Exception" in s
        assert "Hello World!" in s
    else:
        assert False
