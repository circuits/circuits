#!/usr/bin/env python

import pytest

from circuits import Component
from circuits.net.sockets import BUFSIZE, close, write
from circuits.web.controllers import Controller
from circuits.web.websockets import WebSocketClient, WebSocketsDispatcher

from .helpers import urlopen


class Echo(Component):
    channel = 'wsserver'

    def init(self) -> None:
        self.clients = []

    def connect(self, sock, host, port) -> None:
        self.clients.append(sock)
        print('WebSocket Client Connected:', host, port)
        self.fire(write(sock, f'Welcome {host:s}:{port:d}'))

    def disconnect(self, sock) -> None:
        self.clients.remove(sock)

    def read(self, sock, data) -> None:
        self.fire(write(sock, 'Received: ' + data))


class Root(Controller):
    def index(self) -> str:
        return 'Hello World!'


class Client(Component):
    channel = 'ws'

    def init(self, *args, **kwargs) -> None:
        self.response = None

    def read(self, data) -> None:
        self.response = data


@pytest.mark.parametrize('chunksize', [BUFSIZE, BUFSIZE + 1, BUFSIZE * 2])
def test(manager, watcher, webapp, chunksize) -> None:
    echo = Echo().register(webapp)
    assert watcher.wait('registered', channel='wsserver')

    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'

    watcher.clear()

    WebSocketsDispatcher('/websocket').register(webapp)
    assert watcher.wait('registered', channel='web')

    uri = f'ws://{webapp.server.host:s}:{webapp.server.port:d}/websocket'

    WebSocketClient(uri).register(manager)
    client = Client().register(manager)
    assert watcher.wait('registered', channel='wsclient')
    assert watcher.wait('connected', channel='wsclient')

    assert watcher.wait('connect', channel='wsserver')
    assert len(echo.clients) == 1

    assert watcher.wait('read', channel='ws')
    assert client.response.startswith('Welcome')
    watcher.clear()

    client.fire(write('Hello!'), 'ws')
    assert watcher.wait('read', channel='ws')
    assert client.response == 'Received: Hello!'

    watcher.clear()

    client.fire(write('World!'), 'ws')
    assert watcher.wait('read', channel='ws')
    assert client.response == 'Received: World!'

    watcher.clear()

    data = 'A' * (chunksize + 1)
    client.fire(write(data), 'ws')
    assert watcher.wait('read', channel='ws')
    assert client.response == f'Received: {data}'

    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'

    assert len(echo.clients) == 1

    client.fire(close(), 'ws')
    assert watcher.wait('disconnect', channel='wsserver')
    assert len(echo.clients) == 0

    client.unregister()
    assert watcher.wait('unregistered')
