#!/usr/bin/env python

import pytest
pytest.skip("XXX: Broken -- Needs the connect() event to be split from TCPClient or it triggers both the client and the TCPClient when connecting.")

import time

from circuits import Component
from circuits.web.servers import Server
from circuits.web import client
from circuits.net.sockets import write
from circuits.web.controllers import Controller
from circuits.web.websockets import WebSocketClient, WebSocketsDispatcher


class Echo(Component):

    channel = "ws"

    def read(self, sock, data):
        self.fire(write(sock, "Received: " + data))


class Root(Controller):

    def index(self):
        return "Hello World!"


class WSClient(Component):

    response = None

    def ready(self, *args):
        self.fire(client.connect())

    def read(self, data):
        self.response = data


def test1(webapp):
    server = Server(("localhost", 8123))
    Echo().register(server)
    Root().register(server)
    WebSocketsDispatcher("/websocket").register(server)
    server.start()

    client = WebSocketClient("ws://localhost:8123/websocket")
    wsclient = WSClient().register(client)
    waiter = pytest.WaitEvent(client, "connected")
    client.start()
    waiter.wait()
    waiter = pytest.WaitEvent(wsclient, "read")
    client.fire(write("Hello!"), "ws")
    waiter.wait()
    assert wsclient.response == u'Received: Hello!'
    client.stop()

    server.stop()
