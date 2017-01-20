#!/usr/bin/env python
import pytest

from circuits.web import Server
from circuits.web.wsgi import Gateway

from .helpers import urlopen


def hello(environ, start_response):
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    start_response(status, response_headers)
    return "Hello World!"


def foobar(environ, start_response):
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    start_response(status, response_headers)
    return "FooBar!"


@pytest.fixture
def apps(request):
    return {
        "/": hello,
        "/foobar": foobar
    }


def test(apps):
    server = Server(0)
    Gateway(apps).register(server)

    waiter = pytest.WaitEvent(server, "ready")
    server.start()
    waiter.wait()

    f = urlopen(server.http.base)
    s = f.read()
    assert s == b"Hello World!"

    f = urlopen("{0:s}/foobar/".format(server.http.base))
    s = f.read()
    assert s == b"FooBar!"

    server.stop()
