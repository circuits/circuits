#!/usr/bin/env python

import pytest

from circuits import Manager
from circuits.core.pollers import Select
from circuits.net.sockets import Close, Write
from circuits.net.sockets import UDPServer, UDPClient

from .client import Client
from .server import Server


def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"Poller": Select})

    try:
        from circuits.core.pollers import Poll
        Poll()
        metafunc.addcall(funcargs={"Poller": Poll})
    except AttributeError:
        pass

    try:
        from circuits.core.pollers import EPoll
        EPoll()
        metafunc.addcall(funcargs={"Poller": EPoll})
    except AttributeError:
        pass

    try:
        from circuits.core.pollers import KQueue
        KQueue()
        metafunc.addcall(funcargs={"Poller": KQueue})
    except AttributeError:
        pass


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

        client.push(Write((server.host, server.port), b"foo"))
        assert pytest.wait_for(server, "data", b"foo")

        client.push(Close())
        assert pytest.wait_for(client, "closed")

        server.push(Close())
        assert pytest.wait_for(server, "closed")
    finally:
        m.stop()
