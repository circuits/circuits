#!/usr/bin/env python


from __future__ import print_function


from circuits import Component
from circuits.web.servers import Server
from circuits.web.controllers import Controller
from circuits.net.sockets import close, write
from circuits.web.websockets import WebSocketClient, WebSocketsDispatcher


from .helpers import urlopen


class Echo(Component):

    channel = "wsserver"

    def init(self):
        self.clients = []

    def connect(self, sock, host, port):
        self.clients.append(sock)
        print("WebSocket Client Connected:", host, port)
        self.fire(write(sock, "Welcome {0:s}:{1:d}".format(host, port)))

    def disconnect(self, sock):
        self.clients.remove(sock)

    def read(self, sock, data):
        self.fire(write(sock, "Received: " + data))


class Root(Controller):

    def index(self):
        return "Hello World!"


class Client(Component):

    channel = "ws"

    def init(self, *args, **kwargs):
        self.response = None

    def read(self, data):
        self.response = data


def test(manager, watcher, webapp):
    server = Server(0).register(manager)
    watcher.wait("ready")

    echo = Echo().register(server)
    Root().register(server)
    watcher.wait("registered", channel="wsserver")

    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"

    watcher.clear()

    WebSocketsDispatcher("/websocket").register(server)
    watcher.wait("registered", channel="web")

    uri = "ws://{0:s}:{1:d}/websocket".format(server.host, server.port)

    WebSocketClient(uri).register(manager)
    client = Client().register(manager)
    watcher.wait("registered", channel="wsclient")
    watcher.wait("connected", channel="wsclient")

    assert len(echo.clients) == 1

    watcher.wait("read", channel="ws")
    assert client.response.startswith("Welcome")
    watcher.clear()

    client.fire(write("Hello!"), "ws")
    watcher.wait("read", channel="ws")
    assert client.response == "Received: Hello!"

    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"

    assert len(echo.clients) == 1

    client.fire(close(), "ws")
    watcher.wait("disconnect", channel="wsserver")
    assert len(echo.clients) == 0

    client.unregister()
    watcher.wait("unregistered")
    watcher.clear()

    server.unregister()
    watcher.wait("unregistered")
