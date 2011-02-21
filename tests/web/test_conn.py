#!/usr/bin/env python

from httplib import HTTPConnection
from circuits.web import Controller

class Root(Controller):
    def index(self):
        return "Hello World!"

def test(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.auto_open = False
    connection.connect()

    for i in xrange(2):
        connection.request("GET", "/")
        response = connection.getresponse()
        assert response.status == 200
        assert response.reason == "OK"
        assert response.read() == "Hello World!"

    connection.close()
