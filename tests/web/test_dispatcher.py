#!/usr/bin/env python

import pytest

from circuits.web import Controller
from circuits.web.client import Client, Connect, Request


class Root(Controller):
    def __init__(self, *args, **kwargs):
        super(Root, self).__init__(*args, **kwargs)
        self += Leaf()

    def index(self):
        return "Hello World!"

    def name(self):
        return "Earth"


class Leaf(Controller):

    channel = "/world/country/region"

    def index(self):
        return "Hello cities!"

    def city(self):
        return "Hello City!"


def request(webapp, path):
    client = Client(webapp.server.base)
    client.start()

    waiter = pytest.WaitEvent(client, 'connected', channel='client')
    client.fire(Connect())
    assert waiter.wait()

    client.fire(Request("GET", path))
    while client.response is None:
        pass

    client.stop()

    response = client.response
    s = response.read()
    return response.status, s


def test_root(webapp):
    status, content = request(webapp, "/")

    assert status == 200
    assert content == b"Hello World!"


def test_root_name(webapp):
    status, content = request(webapp, "/name")

    assert status == 200
    assert content == b"Earth"


def test_leaf(webapp):
    status, content = request(webapp, "/world/country/region")

    assert status == 200
    assert content == b"Hello cities!"


def test_city(webapp):
    status, content = request(webapp, "/world/country/region/city")

    assert status == 200
    assert content == b"Hello City!"
