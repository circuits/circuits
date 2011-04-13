#!/usr/bin/env python

from circuits import Component
from circuits.net.sockets import TCPServer, Write

class Server(Component):

    def __init__(self, host, port=8000):
        super(Server, self).__init__()

        self._clients = []

        TCPServer((host, port)).register(self)

    def connect(self, sock, host, port):
        self._clients.append(sock)

    def disconnect(self, sock):
        self._clients.remove(sock)

    def read(self, sock, data):
        for client in self._clients:
            if not client == sock:
                self.fire(Write(client, data.strip()))

Server("localhost").run()
