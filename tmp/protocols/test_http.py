#!/usr/bin/env python

from time import sleep

from circuits.web import Server, Controller

from http import Client

class Root(Controller):

    def index(self):
        return "Hello World!"

def test():
    server = Server(8000) + Root()
    server.start()

    client = Client("127.0.0.1", 8000)
    client.start()

    client.connect()
    sleep(1)

    client.request("GET", "/")
    sleep(1)

    response = client.response

    assert response.status == 200
    assert response.reason == "OK"

    s = response.read()
    assert s == "Hello World!"
