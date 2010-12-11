#!/usr/bin/env python

import py

from circuits.core import pollers
from circuits.core.pollers import Select
from circuits.net.sockets import TCPServer, TCPClient
from circuits.net.sockets import Close, Connect, Write

from client import Client
from server import Server

def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"poller": Select, "port": 9000})
    if pollers.HAS_POLL:
        from circuits.core.pollers import Poll
        metafunc.addcall(funcargs={"poller": Poll, "port": 9001})
    if pollers.HAS_EPOLL:
        from circuits.core.pollers import EPoll
        metafunc.addcall(funcargs={"poller": EPoll, "port": 9002})

def test_tcp(poller, port):
    server = Server() + TCPServer(("127.0.0.1", port), poller=poller)
    client = Client() + TCPClient(poller=poller)

    server.start()
    client.start()

    try:
        client.push(Connect("127.0.0.1", port))
        py.test.wait_for(client, "connected")
        py.test.wait_for(server, "connected")
        py.test.wait_for(client, "data", "Ready")

        client.push(Write("foo"))
        py.test.wait_for(server, "data", "foo")

        client.push(Close())
        server.push(Close())
        py.test.wait_for(client, "disconnected")
        py.test.wait_for(server, "disconnected")
    finally:
        server.stop()
        client.stop()
