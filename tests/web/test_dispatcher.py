#!/usr/bin/env python
from circuits.web import Controller
from circuits.web.client import Client, request


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


def make_request(webapp, path):
    client = Client()
    client.start()

    client.fire(request("GET", path))
    while client.response is None:
        pass

    client.stop()

    response = client.response
    s = response.read()
    return response.status, s


def test_root(webapp):
    status, content = make_request(webapp, webapp.server.http.base)

    assert status == 200
    assert content == b"Hello World!"


def test_root_name(webapp):
    status, content = make_request(webapp, "%s/name" % webapp.server.http.base)

    assert status == 200
    assert content == b"Earth"


def test_leaf(webapp):
    status, content = make_request(
        webapp, "%s/world/country/region" % webapp.server.http.base)

    assert status == 200
    assert content == b"Hello cities!"


def test_city(webapp):
    status, content = make_request(
        webapp, "%s/world/country/region/city" % webapp.server.http.base)

    assert status == 200
    assert content == b"Hello City!"
