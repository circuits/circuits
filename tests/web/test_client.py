#!/usr/bin/env python

import pytest

from circuits.web import Server, Controller

from circuits.web.client import Client, Connect, Request

class Root(Controller):

    def index(self):
        return "Hello World!"

def test(webapp):
    client = Client(webapp.server.base)
    client.start()

    waiter = pytest.WaitEvent(client, 'connected', channel=client.channel)
    client.fire(Connect())
    assert waiter.wait()

    client.fire(Request("GET", "/"))
    while client.response is None: pass

    client.stop()

    response = client.response
    assert response.status == 200
    assert response.message == "OK"

    s = response.read()
    assert s == b"Hello World!"

def test_named(webapp):
    client = Client(webapp.server.base, channel="Client2")
    client.start()

    waiter = pytest.WaitEvent(client, 'connected', channel=client.channel)
    client.fire(Connect())
    assert waiter.wait()

    client.fire(Request("GET", "/"))
    while client.response is None: pass

    client.stop()

    response = client.response
    assert response.status == 200
    assert response.message == "OK"

    s = response.read()
    assert s == b"Hello World!"
