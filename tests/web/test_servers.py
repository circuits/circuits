#!/usr/bin/env python

import pytest

from os import path
from socket import gaierror

from circuits import Component
from circuits.web import Controller
from circuits.web import BaseServer, Server

from .helpers import urlopen, URLError

CERTFILE = path.join(path.dirname(__file__), "cert.pem")


class BaseRoot(Component):

    channel = "web"

    def request(self, request, response):
        return "Hello World!"


class Root(Controller):

    def index(self):
        return "Hello World!"


def test_baseserver():
    server = BaseServer(0)
    BaseRoot().register(server)
    server.start()

    try:
        f = urlopen(server.base)
    except URLError as e:
        if type(e[0]) is gaierror:
            f = urlopen("http://127.0.0.1:9000")
        else:
            raise

    s = f.read()
    assert s == b"Hello World!"


def test_server():
    server = Server(0)
    Root().register(server)
    server.start()

    try:
        f = urlopen(server.base)
    except URLError as e:
        if type(e[0]) is gaierror:
            f = urlopen("http://127.0.0.1:9000")
        else:
            raise

    s = f.read()
    assert s == b"Hello World!"


def test_secure_server():
    pytest.importorskip("ssl")

    server = Server(0, secure=True, certfile=CERTFILE)
    Root().register(server)
    server.start()

    try:
        f = urlopen(server.base)
    except URLError as e:
        if type(e[0]) is gaierror:
            f = urlopen("http://127.0.0.1:9000")
        else:
            raise

    s = f.read()
    assert s == b"Hello World!"


def test_unixserver(tmpdir):
    sockpath = tmpdir.ensure("test.sock")
    socket = str(sockpath)
    server = Server(socket)
    Root().register(server)
    server.start()

    assert path.basename(server.host) == "test.sock"

    server.stop()
