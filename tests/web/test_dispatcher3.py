#!/usr/bin/env python
from http.client import HTTPConnection

import pytest

from circuits.web import Controller


class Root(Controller):
    def GET(self):
        return 'GET'

    def PUT(self):
        return 'PUT'

    def POST(self):
        return 'POST'

    def DELETE(self):
        return 'DELETE'


@pytest.mark.parametrize(('method'), ['GET', 'PUT', 'POST', 'DELETE'])
def test(webapp, method):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    connection.request(method, '/')
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == 'OK'

    s = response.read()
    assert s == f'{method:s}'.encode()

    connection.close()
