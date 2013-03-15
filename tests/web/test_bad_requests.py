#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection  # NOQA

from circuits.six import b
from circuits.web import Controller


class Root(Controller):

    def index(self):
        return "Hello World!"


def test_bad_header(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    connection.putrequest("GET", "/", "HTTP/1.1")
    connection.putheader("Connection", "close")
    connection._output("X-Foo")  # Bad Header
    connection.endheaders()

    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"
    s = response.read()
    assert s == b("Hello World!")

    connection.close()
