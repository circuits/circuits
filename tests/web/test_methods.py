#!/usr/bin/env python
try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection  # NOQA

from circuits.web import Controller


class Root(Controller):

    def index(self):
        return "Hello World!"


def test_GET(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)

    connection.request("GET", "/")
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"
    s = response.read()
    assert s == b"Hello World!"


def test_HEAD(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)

    connection.request("HEAD", "/")
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"
    s = response.read()
    assert s == b""
