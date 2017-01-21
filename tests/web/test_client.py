#!/usr/bin/env python
from circuits.web import Controller
from circuits.web.client import Client, request


class Root(Controller):

    def index(self):
        return "Hello World!"


def test(webapp):
    client = Client()
    client.start()

    client.fire(request("GET", webapp.server.http.base))
    while client.response is None:
        pass

    client.stop()

    response = client.response
    assert response.status == 200
    assert response.reason == "OK"

    s = response.read()
    assert s == b"Hello World!"
