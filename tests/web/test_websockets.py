#!/usr/bin/env python

import pytest
pytest.skip("Not passing")

from urllib.parse import urlunsplit

from circuits import Component
from circuits.net.sockets import Write
from circuits.web.dispatchers import WebSockets

from .websocket import create_connection


class Test1(Component):

    channel = "ws"

    def message(self, sock, data):
        self.push(Write(sock, data))


class Test2(Component):

    channel = "ws"

    def message(self, sock, data):
        return data


def test1(webapp):
    Test1().register(webapp)
    WebSockets("/websocket").register(webapp)

    host = webapp.server.host
    if webapp.server.port is not 80:
        host = "%s:%d" % (host, webapp.server.port)

    url = urlunsplit(("ws", host, "/websocket", "", ""))

    ws = create_connection(url)
    ws.send("Hello World!")
    result =  ws.recv()
    assert result == "Hello World!"
    ws.close()
