#!/usr/bin/env python


from __future__ import print_function

import sys

from circuits import Component, Debugger
from circuits.net.sockets import TCPClient
from circuits.net.events import connect, write


class App(Component):

    def init(self, host=None, port="443"):
        self.host = host or "www.google.com"
        self.port = int(port)

        TCPClient().register(self)

    def ready(self, *args):
        self.fire(connect(self.host, self.port, True))

    def connected(self, *args):
        self.fire(write("GET / HTTP/1.1\r\nHost: www.google.com\r\nConnection: close\r\n\r\n"))

    def read(self, data):
        print(data)

    def disconnected(self, *args):
        raise SystemExit(0)


app = App(*sys.argv[1:]) + Debugger()
app.run()
