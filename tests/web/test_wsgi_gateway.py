#!/usr/bin/env python

from urllib2 import urlopen

from circuits.web.wsgi import Application, Gateway

def app(environ, start_response):
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    start_response(status, response_headers)
    return "Hello World!"

def test(webapp):
    gateway = Gateway(app)
    gateway.register(webapp)

    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"

    gateway.unregister()
