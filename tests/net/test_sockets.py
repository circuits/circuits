# Module:   sockets
# Date:     26th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Sockets Tests"""

import os
from time import sleep

from circuits import Component
from circuits.net.sockets import TCPServer, TCPClient
from circuits.net.sockets import UDPServer, UDPClient
from circuits.net.sockets import UNIXServer, UNIXClient
from circuits.net.sockets import Close, Connect, Write, Pipe

class Client(Component):

    channel = "client"

    def __init__(self):
        super(Client, self).__init__()

        self.data = ""
        self.connected = False
        self.disconnected = False

    def connected(self, host, port):
        self.connected = True

    def disconnected(self):
        self.disconnected = True

    def read(self, data):
        self.data = data

class Server(Component):

    channel = "server"

    def __init__(self):
        super(Server, self).__init__()

        self.data = ""
        self.connected = False
        self.disconnected = False

    def connect(self, sock, *args):
        self.connected = True
        self.push(Write(sock, "Ready"))

    def disconnect(self, sock):
        self.disconnected = True

    def read(self, sock, data):
        self.data = data

def test_tcp():
    server = Server() + TCPServer(9999)
    client = Client() + TCPClient()

    server.start()
    client.start()

    try:
        client.push(Connect("127.0.0.1", 9999))
        sleep(1)
        assert client.connected
        assert server.connected
        assert client.data == "Ready"

        client.push(Write("foo"))
        sleep(1)
        assert server.data == "foo"

        client.push(Close())
        sleep(1)
        assert client.disconnected
        assert server.disconnected
    finally:
        server.stop()
        client.stop()

def test_udp():
    server = Server() + UDPServer(9999)
    client = Client() + UDPClient(10000, channel="client")

    server.start()
    client.start()

    try:
        client.push(Write(("127.0.0.1", 9999), "foo"))
        sleep(1)
        assert server.data == "foo"
    finally:
        server.stop()
        client.stop()

def test_unix():
    filename = os.path.join(os.path.abspath(os.getcwd()), "test.sock")
    server = Server() + UNIXServer(filename)
    client = Client() + UNIXClient()

    server.start()
    client.start()

    try:
        client.push(Connect(filename))
        sleep(1)
        assert client.connected
        assert server.connected
        assert client.data == "Ready"

        client.push(Write("foo"))
        sleep(1)
        assert server.data == "foo"

        client.push(Close())
        sleep(1)
        assert client.disconnected
        assert server.disconnected
    finally:
        server.stop()
        client.stop()
        os.remove(filename)

def test_pipe():
    a, b = Pipe(("client", "client",))
    a = Client() + a
    b = Client() + b

    a.start()
    b.start()

    try:
        a.push(Write("foo"))
        sleep(1)
        assert b.data == "foo"

        b.push(Write("foo"))
        sleep(1)
        assert a.data == "foo"

        a.push(Close())
        sleep(1)
        assert a.disconnected
        assert b.disconnected
    finally:
        a.stop()
        b.stop()
