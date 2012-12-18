#!/usr/bin/env python

import pytest
import socket

from circuits import Manager
from circuits.core.pollers import Select
from circuits.core.events import Unregister
from circuits.net.sockets import Close, Write
from circuits.net.sockets import UDPServer, UDPClient, UDP6Server, UDP6Client

from .client import Client
from .server import Server


def wait_host(server):
    def checker(obj, attr):
        return all((getattr(obj, a) for a in attr))
    assert pytest.wait_for(server, ("host", "port"), checker)


def _pytest_generate_tests(metafunc, ipv6):
    metafunc.addcall(funcargs={"Poller": Select, "ipv6": ipv6})

    try:
        from circuits.core.pollers import Poll
        Poll()
        metafunc.addcall(funcargs={"Poller": Poll, "ipv6": ipv6})
    except AttributeError:
        pass

    try:
        from circuits.core.pollers import EPoll
        EPoll()
        metafunc.addcall(funcargs={"Poller": EPoll, "ipv6": ipv6})
    except AttributeError:
        pass

    try:
        from circuits.core.pollers import KQueue
        KQueue()
        metafunc.addcall(funcargs={"Poller": KQueue, "ipv6": ipv6})
    except AttributeError:
        pass


def pytest_generate_tests(metafunc):
    _pytest_generate_tests(metafunc, ipv6=False)
    if socket.has_ipv6:
        _pytest_generate_tests(metafunc, ipv6=True)


def test_udp_basic(Poller, ipv6):
    m = Manager() + Poller()

    if ipv6:
        udp_server = UDP6Server(0)
        udp_client = UDP6Client(0, channel="client")
    else:
        udp_server = UDPServer(0)
        udp_client = UDPClient(0, channel="client")
    server = Server() + udp_server
    client = Client() + udp_client

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


def test_udp_close(Poller, ipv6):
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
