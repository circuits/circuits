#!/usr/bin/env python

from circuits import Component
from circuits.web.dispatchers import WebSockets
from circuits.web import Server, Controller, Logger
from circuits.net.sockets import Write


class Echo(Component):

    channel = "ws"

    def read(self, sock, data):
        self.fireEvent(Write(sock, "Received: " + data))


class Root(Controller):

    def index(self):
        return "Hello World!"

(
    Server(("0.0.0.0", 8000))
    + Echo()
    + Root()
    + Logger()
    + WebSockets("/websocket")
).run()
