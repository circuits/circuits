#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection  # NOQA

from circuits.six import b, u
from circuits.web import Controller
from circuits.web.client import Client, Request, Connect

from .helpers import urlopen


class Root(Controller):

    def index(self):
        return "Hello World!"

    def request_body(self):
        return self.request.body.read()

    def response_body(self):
        return u("ä")

    def request_headers(self):
        return self.request.headers["A"]

    def response_headers(self):
        self.response.headers["A"] = "ä"
        return u("ä")


def test_index(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == b("Hello World!")


def test_request_body(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    body = b("ä")
    connection.request("GET", "/request_body", body)
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"
    s = response.read()
    assert s == b("ä")

    connection.close()


def test_response_body(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    connection.request("GET", "/response_body")
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"
    s = response.read()
    assert s == b("ä")

    connection.close()


def test_request_headers(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    body = b("")
    headers = {"A": b("ä")}
    connection.request("GET", "/request_headers", body, headers)
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"
    s = response.read()
    assert s == b("ä")

    connection.close()


def test_response_headers(webapp):
    client = Client('http://%s:%s' % (webapp.server.host, webapp.server.port))
    client.start()
    waiter = pytest.WaitEvent(client, 'connected', channel=client.channel)
    client.fire(Connect())
    assert waiter.wait()
    client.fire(Request("GET", "/response_headers"))
    while client.response is None:
        pass
    assert client.response.status == 200
    assert client.response.message == 'OK'
    s = client.response.read()
    a = client.response.headers.get('A')
    assert a == u("ä")
    assert s == b("ä")
