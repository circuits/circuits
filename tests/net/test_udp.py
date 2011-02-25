#!/usr/bin/env python

import pytest

from circuits import Manager
from circuits.core import pollers
from circuits.net.sockets import Close, Write
from circuits.net.sockets import UDPServer, UDPClient

from client import Client
from server import Server

def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"Poller": pollers.Select})
    if pollers.HAS_POLL:
        metafunc.addcall(funcargs={"Poller": pollers.Poll})
    if pollers.HAS_EPOLL:
        metafunc.addcall(funcargs={"Poller": pollers.EPoll})

def test_udp(Poller):
    m = Manager() + Poller()

    server = Server() + UDPServer(0)
    client = Client() + UDPClient(0, channel="client")

    server.register(m)
    client.register(m)

    m.start()

    try:
        assert pytest.wait_for(server, "ready")
        assert pytest.wait_for(client, "ready")

        client.push(Write((server.host, server.port), "foo"))
        assert pytest.wait_for(server, "data", "foo")
    finally:
        m.stop()
