#!/usr/bin/env python

from time import time

import pytest

from circuits import Manager
from circuits.core.pollers import Select, TIMEOUT
from circuits.net.sockets import TCPServer, TCPClient
from circuits.net.sockets import Close, Connect, Write

from client import Client
from server import Server

def test():
    m = Manager()
    m.start()

    Select().register(m)

    server = (Server() + TCPServer(("0.0.0.0", 8000)))
    client = (Client() + TCPClient())

    server.register(m)
    client.register(m)

    assert pytest.wait_for(client, "ready")
    assert pytest.wait_for(server, "ready")

    m.push(Connect("127.0.0.1", 8000), target="client")
    assert pytest.wait_for(client, "connected")
    assert pytest.wait_for(server, "connected")
    assert pytest.wait_for(client, "data", "Ready")

    m.push(Write("foo"), target="client")
    assert pytest.wait_for(server, "data", "foo")

    m.push(Close(), target="client")
    assert pytest.wait_for(client, "disconnected")

    m.push(Close(), target="server")
    assert pytest.wait_for(server, "disconnected")

    m.stop()
