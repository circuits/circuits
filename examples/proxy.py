#!/usr/bin/env python
from uuid import uuid4 as uuid

from circuits import Component, Debugger
from circuits.net.events import close, connect, write
from circuits.net.sockets import TCPClient, TCPServer


class Client(Component):

    channel = "client"

    def init(self, sock, host, port, channel=channel):
        self.sock = sock
        self.host = host
        self.port = port

        TCPClient(channel=self.channel).register(self)

    def ready(self, *args):
        self.fire(connect(self.host, self.port))

    def disconnect(self, *args):
        self.fire(close(self.sock), self.parent.channel)

    def read(self, data):
        self.fire(write(self.sock, data), self.parent.channel)


class Proxy(Component):

    channel = "server"

    def init(self, bind, host, port):
        self.bind = bind
        self.host = host
        self.port = port

        self.clients = dict()

        TCPServer(self.bind).register(self)

    def connect(self, sock, host, port):
        channel = uuid()

        client = Client(
            sock, self.host, self.port, channel=channel
        ).register(self)

        self.clients[sock] = client

    def disconnect(self, sock):
        client = self.clients.get(sock)
        if client is not None:
            client.unregister()
            del self.clients[sock]

    def read(self, sock, data):
        client = self.clients[sock]
        self.fire(write(data), client.channel)


app = Proxy(("0.0.0.0", 3333), "127.0.0.1", 22)

Debugger().register(app)

app.run()
