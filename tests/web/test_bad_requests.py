#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest


try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection  # NOQA


from circuits.web import Controller


class Root(Controller):

    def index(self):
        return "Hello World!"


def test_bad_header(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    connection.putrequest("GET", "/", "HTTP/1.1")
    connection.putheader("Connection", "close")
    if pytest.PYVER[0] == 3:
        connection._output("X-Foo".encode("utf-8"))  # Bad Header
    else:
        connection._output("X-Foo")  # Bad Header

    connection.endheaders()

    response = connection.getresponse()
    assert response.status == 400
    assert response.reason == "Bad Request"

    connection.close()
