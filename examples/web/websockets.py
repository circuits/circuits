#!/usr/bin/env python

from circuits import Component
from circuits.web.dispatchers import WebSockets
from circuits.web import Server, Controller, Logger


class Echo(Component):

    channel = "ws"

    def message(self, sock, data):
        return data


class Root(Controller):

    def index(self):
        return "Hello World!"

(Server(("0.0.0.0", 8000))
        + Echo()
        + Root()
        + Logger()
        + WebSockets("/websocket")
).run()
