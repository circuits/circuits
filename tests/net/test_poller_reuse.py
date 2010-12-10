#!/usr/bin/env python

from time import time

import py
py.test.skip("XXX: Not passing...")

from circuits import Manager
from circuits.core.pollers import Select, TIMEOUT
from circuits.net.sockets import TCPServer, TCPClient
from circuits.net.sockets import Close, Connect, Write

from client import Client
from server import Server

TIMEOUT += 0.1

def test():
    m = Manager()
    m += Select()

    server = (Server() + TCPServer(8000))
    client = (Client() + TCPClient())

    m += server
    m += client

    def tick(m, timeout=TIMEOUT):
        t = time() + timeout
        while time() < t:
            m.tick()

    tick(m)

    m.push(Connect("127.0.0.1", 8000), target="client")
    tick(m)
    client_connected = client.connected
    server_connected = server.connected
    s = client.data
    assert client_connected
    assert server_connected
    assert s == "Ready"

    m.push(Write("foo"), target="client")
    tick(m)
    s = server.data
    assert s == "foo"

    m.push(Close(), target="client")
    tick(m)
    m.push(Close(), target="server")
    tick(m)
    client_disconnected = client.disconnected
    server_disconnected = server.disconnected
    assert client_disconnected
    assert server_disconnected
