#!/usr/bin/env python

import pytest
if pytest.PY3:
    pytest.skip("Broken on Python 3")

from circuits.web.servers import Server

from circuits import Component
from circuits.net.sockets import Write
from circuits.web.dispatchers import WebSockets
from circuits.web.controllers import Controller
from circuits.web.websocket import WebSocketClient
from circuits.web.client import Connect
import time


class Echo(Component):

    channel = "ws"

    def read(self, sock, data):
        self.fireEvent(Write(sock, "Received: " + data))

class Root(Controller):

    def index(self):
        return "Hello World!"

class WSClient(Component):
    
    response = None
    
    def read(self, data):
        self.response = data


def test1(webapp):
    server = Server(("localhost", 8123)) 
    Echo().register(server)
    Root().register(server)
    WebSockets("/websocket").register(server)
    server.start()

    client = WebSocketClient("ws://localhost:8123/websocket")
    wsclient = WSClient().register(client)
    client.start()
    client.fire(Connect())
    client.fire(Write("Hello!"), "ws")
    for i in range(100):
        if wsclient.response is not None:
            break
        time.sleep(0.010)
    assert wsclient.response is not None
    client.stop()

    server.stop()
