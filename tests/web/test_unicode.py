#!/usr/bin/env python

from http.client import HTTPConnection

import pytest

from circuits.web import Controller
from circuits.web.client import Client, request

from .helpers import urlopen


class Root(Controller):
    def index(self):
        return 'Hello World!'

    def request_body(self):
        return self.request.body.read()

    def response_body(self):
        return 'ä'

    def request_headers(self):
        return self.request.headers['A']

    def response_headers(self):
        self.response.headers['A'] = 'ä'
        return 'ä'

    def argument(self, arg):
        return arg


def test_index(webapp):
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'


@pytest.mark.parametrize(
    'body',
    [
        'ä'.encode(),
        'ä'.encode('iso8859-1'),
    ],
)
def test_request_body(webapp, body):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    connection.request('POST', '/request_body', body)
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == 'OK'
    s = response.read()
    assert s == body

    connection.close()


def test_response_body(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    connection.request('GET', '/response_body')
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == 'OK'
    s = response.read()
    assert s == 'ä'.encode()

    connection.close()


def test_request_headers(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    body = b''
    headers = {'A': 'ä'}
    connection.request('GET', '/request_headers', body, headers)
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == 'OK'
    s = response.read()
    assert s == 'ä'.encode()

    connection.close()


def test_response_headers(webapp):
    client = Client()
    client.start()
    client.fire(
        request(
            'GET',
            'http://%s:%s/response_headers'
            % (
                webapp.server.host,
                webapp.server.port,
            ),
        ),
    )

    while client.response is None:
        pass
    assert client.response.status == 200
    assert client.response.reason == 'OK'
    s = client.response.read()
    a = client.response.headers.get('A')
    assert a == 'ä'
    assert s == 'ä'.encode()


def test_argument(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    data = 'arg=%E2%86%92'
    connection.request('POST', '/argument', data, {'Content-type': 'application/x-www-form-urlencoded'})
    response = connection.getresponse()
    assert response.status == 200
    assert response.reason == 'OK'
    s = response.read()
    assert s.decode('utf-8') == '\u2192'

    connection.close()
