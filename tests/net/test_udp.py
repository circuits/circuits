#!/usr/bin/env python

from time import sleep

import pytest

from circuits import Manager
from circuits.tools import kill
from circuits.core.pollers import Select
from circuits.core.events import Unregister
from circuits.net.sockets import Close, Write
from circuits.net.sockets import UDPServer, UDPClient

from .client import Client
from .server import Server


def wait_host(server):
    def checker(obj, attr):
        return all((getattr(obj, a) for a in attr))
    assert pytest.wait_for(server, ("host", "port"), checker)


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
        wait_host(server)

        client.fire(Write((server.host, server.port), b"foo"))
        assert pytest.wait_for(server, "data", b"foo")

        client.fire(Close())
        assert pytest.wait_for(client, "closed")

        server.fire(Close())
        assert pytest.wait_for(server, "closed")
    finally:
        m.stop()

def test_udp_close(Poller):
    m = Manager() + Poller()
    server = Server() + UDPServer(0)
    server.register(m)
    m.start()

    try:
        assert pytest.wait_for(server, "ready")
        wait_host(server)

        host, port = server.host, server.port

        server.fire(Close())
        assert pytest.wait_for(server, "disconnected")

        server.fire(Unregister(server))
        def test(obj, attr):
            return attr not in obj.components
        assert pytest.wait_for(m, server, value=test)

        server = Server() + UDPServer((host, port))
        server.register(m)

        assert pytest.wait_for(server, "ready", timeout=30.0)
    finally:
        m.stop()
