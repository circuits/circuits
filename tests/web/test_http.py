#!/usr/bin/env python

import pytest

from circuits import Component
from circuits.web import Controller
from circuits.web.client import parse_url
from circuits.net.sockets import TCPClient
from circuits.net.events import connect, write


class Client(Component):

    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self._buffer = []
        self.done = False

    def read(self, data):
        self._buffer.append(data)
        if data.find(b"\r\n") != -1:
            self.done = True

    def buffer(self):
        return b''.join(self._buffer)


class Root(Controller):

    def index(self):
        return "Hello World!"


def test(webapp):
    transport = TCPClient()
    client = Client()
    client += transport
    client.start()

    host, port, resource, secure = parse_url(webapp.server.http.base)
    client.fire(connect(host, port))
    assert pytest.wait_for(transport, "connected")

    client.fire(write(b"GET / HTTP/1.1\r\n"))
    client.fire(write(b"Content-Type: text/plain\r\n\r\n"))
    assert pytest.wait_for(client, "done")

    client.stop()

    s = client.buffer().decode('utf-8').split('\r\n')[0]
    assert s == "HTTP/1.1 200 OK"
