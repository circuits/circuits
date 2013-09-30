#!/usr/bin/env python

import pytest
pytest.skip("XXX: Still broken :/")

from circuits import Component
from circuits.net.sockets import write
from circuits.web.servers import Server
from circuits.web.controllers import Controller
from circuits.web.websockets import WebSocketClient, WebSocketsDispatcher


class Echo(Component):

    channel = "ws"

    def read(self, sock, data):
        self.fire(write(sock, "Received: " + data))


class Root(Controller):

    def index(self):
        return "Hello World!"


class Client(WebSocketClient):

    def init(self, *args, **kwargs):
        self.response = None

    def read(self, data):
        self.response = data


def test(manager, watcher):
    server = Server(("localhost", 8123)).register(manager)
    watcher.wait("ready")

    Echo().register(server)
    Root().register(server)
    WebSocketsDispatcher("/websocket").register(server)

    client = WebSocketClient("ws://localhost:8123/websocket").register(manager)
    watcher.wait("connected")

    client.fire(write("Hello!"), "ws")
    watcher.wait("read")
    assert client.response == "Received: Hello!"

    client.unregister()
    watcher.wait("unregistered")

    server.unregister()
    watcher.wait("unregistered")
