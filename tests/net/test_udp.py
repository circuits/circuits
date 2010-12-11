#!/usr/bin/env python

import py

from circuits.core import pollers
from circuits.net.sockets import Write
from circuits.core.pollers import Select
from circuits.net.sockets import UDPServer, UDPClient

from client import Client
from server import Server

def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"poller": Select, "ports": (10000, 10001)})
    if pollers.HAS_POLL:
        from circuits.core.pollers import Poll
        metafunc.addcall(funcargs={"poller": Poll, "ports": (10002, 10003)})
    if pollers.HAS_EPOLL:
        from circuits.core.pollers import EPoll
        metafunc.addcall(funcargs={"poller": EPoll, "ports": (10004, 10005)})

def test_udp(poller, ports):
    server = Server() + UDPServer(("127.0.0.1", ports[0]), poller=poller)
    client = Client() + UDPClient(("127.0.0.1", ports[1]), poller=poller,
            channel="client")

    server.start()
    client.start()

    try:
        client.push(Write(("127.0.0.1", ports[0]), "foo"))
        py.test.wait_for(server, "data", "foo")
    finally:
        server.stop()
        client.stop()
