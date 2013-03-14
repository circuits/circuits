#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection  # NOQA

from circuits.web import Controller

from .helpers import urlopen


class Root(Controller):

    def index(self):
        return "Hello World!"

    def request_body(self):
        return self.request.body.read()

    def response_body(self):
        return u"ä"

    def request_headers(self):
        return self.request.headers["A"]

    def response_headers(self):
        self.response.headers["A"] = u"ä"
        return u"ä"


def test_index(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"


def test_request_body(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    body = u"ä".encode("utf-8")
    connection.request("GET", "/request_body", body)
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"
    s = response.read().decode("utf-8")
    assert s == u"ä"

    connection.close()


def test_response_body(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    connection.request("GET", "/response_body")
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"
    s = response.read().decode("utf-8")
    assert s == u"ä"

    connection.close()


def test_request_headers(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    body = b""
    headers = {"A": u"ä".encode("utf-8")}
    connection.request("GET", "/request_headers", body, headers)
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"
    s = response.read().decode("utf-8")
    assert s == u"ä"

    connection.close()


def test_response_headers(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    body = b""
    headers = {}
    connection.request("GET", "/response_headers", body, headers)
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == "OK"
    a = response.getheader("A").decode("utf-8")
    s = response.read().decode("utf-8")
    assert a == u"ä"
    assert s == u"ä"

    connection.close()
