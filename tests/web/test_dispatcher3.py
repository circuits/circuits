#!/usr/bin/env python
import pytest

from circuits.web import Controller

try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection  # NOQA


class Root(Controller):

    def GET(self):
        return "GET"

    def PUT(self):
        return "PUT"

    def POST(self):
        return "POST"

    def DELETE(self):
        return "DELETE"


@pytest.mark.parametrize(("method"), ["GET", "PUT", "POST", "DELETE"])
def test(webapp, method):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    connection.request(method, "/")
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"

    s = response.read()
    assert s == "{0:s}".format(method).encode("utf-8")

    connection.close()
