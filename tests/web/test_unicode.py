#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest


try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection  # NOQA


from circuits.web import Controller
from circuits.web.client import Client, request

from .helpers import urlopen


class Root(Controller):

    def index(self):
        return "Hello World!"

    def request_body(self):
        return self.request.body.read()

    def response_body(self):
        return "ä"

    def request_headers(self):
        return self.request.headers["A"]

    def response_headers(self):
        self.response.headers["A"] = "ä"
        return "ä"


def test_index(webapp):
    f = urlopen(webapp.server.http.base)
    s = f.read()

    if pytest.PYVER[0] == 3:
        assert s == "Hello World!".encode("utf-8")
    else:
        assert s == "Hello World!"


def test_request_body(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    body = u"ä".encode("utf-8")

    connection.request("GET", "/request_body", body)
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"
    s = response.read()
    assert s == u"ä".encode("utf-8")

    connection.close()


def test_response_body(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    connection.request("GET", "/response_body")
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"
    s = response.read()
    assert s == u"ä".encode("utf-8")

    connection.close()


def test_request_headers(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    body = u"".encode("utf-8")
    headers = {"A": "ä"}
    connection.request("GET", "/request_headers", body, headers)
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"
    s = response.read()
    assert s == u"ä".encode("utf-8")

    connection.close()


def test_response_headers(webapp):
    client = Client()
    client.start()
    client.fire(
        request(
            "GET",
            "http://%s:%s/response_headers" % (
                webapp.server.host, webapp.server.port
            )
        )
    )

    while client.response is None:
        pass
    assert client.response.status == 200
    assert client.response.reason == 'OK'
    s = client.response.read()
    a = client.response.headers.get('A')
    assert a == u"ä".encode("utf-8")
    assert s == u"ä".encode("utf-8")
