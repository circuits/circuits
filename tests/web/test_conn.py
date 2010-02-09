#!/usr/bin/env python

from httplib import HTTPConnection

from circuits.web import Server, Controller

class Root(Controller):

    def index(self):
        return "Hello World!"

app = Server(8000) + Root()

def test():
    connection = HTTPConnection("localhost", 8000)
    connection.auto_open = False
    connection.connect()

    for i in xrange(2):
        connection.request("GET", "/")
        response = connection.getresponse()
        assert response.status == 200
        assert response.reason == "OK"
        assert response.read() == "Hello World!"

    connection.close()

def pytest_session_finish():
    app.stop()
