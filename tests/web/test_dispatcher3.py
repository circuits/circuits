#!/usr/bin/env python
import pytest

from circuits.web import Controller

from http.client import HTTPConnection


class Root(Controller):

    async def GET(self):
        return "GET"

    async def PUT(self):
        return "PUT"

    async def POST(self):
        return "POST"

    async def DELETE(self):
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
    assert s == f"{method:s}".encode()

    connection.close()
