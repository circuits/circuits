#!/usr/bin/env python
from http.client import HTTPConnection

from circuits.web import Controller


class Root(Controller):
    def index(self):
        return 'Hello World!'


def test(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.auto_open = False
    connection.connect()

    for _i in range(2):
        connection.request('GET', '/')
        response = connection.getresponse()
        assert response.status == 200
        assert response.reason == 'OK'
        s = response.read()
        assert s == b'Hello World!'

    connection.close()
