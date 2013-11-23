#!/usr/bin/env python

from circuits.net.events import write
from circuits import Component, Debugger
from circuits.web.dispatchers import WebSockets
from circuits.web import Controller, Logger, Server, Static


class Echo(Component):

    channel = "ws"

    def read(self, sock, data):
        self.fireEvent(write(sock, "Received: " + data))


class Root(Controller):

    def index(self):
        return "Hello World!"

app = Server(("0.0.0.0", 8000))
Debugger().register(app)
Static().register(app)
Echo().register(app)
Root().register(app)
Logger().register(app)
WebSockets("/websocket").register(app)
app.run()
