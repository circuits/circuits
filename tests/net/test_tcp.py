#!/usr/bin/env python

from time import time
from random import seed, randint

import pytest

from circuits import Manager
from circuits.core.pollers import Select
from circuits.net.sockets import TCPServer, TCPClient
from circuits.net.sockets import Close, Connect, Write

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


def test_tcp_basic(Poller):
    m = Manager() + Poller()

    server = Server() + TCPServer(0)
    client = Client() + TCPClient()

    server.register(m)
    client.register(m)

    m.start()

    try:
        assert pytest.wait_for(client, "ready")
        assert pytest.wait_for(server, "ready")

        client.push(Connect(server.host, server.port))
        assert pytest.wait_for(client, "connected")
        assert pytest.wait_for(server, "connected")
        assert pytest.wait_for(client, "data", b"Ready")

        client.push(Write(b"foo"))
        assert pytest.wait_for(server, "data", b"foo")

        client.push(Close())
        assert pytest.wait_for(client, "disconnected")
        assert pytest.wait_for(server, "disconnected")

        server.push(Close())
        assert pytest.wait_for(server, "closed")
    finally:
        m.stop()


def test_tcp_reconnect(Poller):
    m = Manager() + Poller()
    server = Server() + TCPServer(0)
    client = Client() + TCPClient()

    server.register(m)
    client.register(m)

    m.start()

    try:
        assert pytest.wait_for(client, "ready")
        assert pytest.wait_for(server, "ready")

        # 1st connect
        client.push(Connect(server.host, server.port))
        assert pytest.wait_for(client, "connected")
        assert pytest.wait_for(server, "connected")
        assert pytest.wait_for(client, "data", b"Ready")

        client.push(Write(b"foo"))
        assert pytest.wait_for(server, "data", b"foo")

        # disconnect
        client.push(Close())
        assert pytest.wait_for(client, "disconnected")

        # 2nd reconnect
        client.push(Connect(server.host, server.port))
        assert pytest.wait_for(client, "connected")
        assert pytest.wait_for(server, "connected")
        assert pytest.wait_for(client, "data", b"Ready")

        client.push(Write(b"foo"))
        assert pytest.wait_for(server, "data", b"foo")

        client.push(Close())
        assert pytest.wait_for(client, "disconnected")
        assert pytest.wait_for(server, "disconnected")

        server.push(Close())
        assert pytest.wait_for(server, "closed")
    finally:
        m.stop()


def test_tcp_connect_closed_port(Poller):
    m = Manager() + Poller()
    tcp_server = TCPServer(0)
    server = Server() + tcp_server
    client = Client() + TCPClient()

    server.register(m)
    client.register(m)

    m.start()

    try:
        assert pytest.wait_for(client, "ready")
        assert pytest.wait_for(server, "ready")

        host, port = server.host, server.port
        tcp_server._sock.close()

        # 1st connect
        client.push(Connect(host, port))
        assert pytest.wait_for(client, "connected")

        client.push(Write(b"foo"))
        assert pytest.wait_for(client, "disconnected")

        client.disconnected = False
        client.push(Write(b"foo"))
        assert pytest.wait_for(client, "disconnected", timeout=1.0) is None
    finally:
        m.stop()


def test_tcp_bind(Poller):
    m = Manager() + Poller()

    seed(time())
    bind_port = randint(1000, 65535)

    server = Server() + TCPServer(0)
    client = Client() + TCPClient(bind_port)

    server.register(m)
    client.register(m)

    m.start()

    try:
        assert pytest.wait_for(client, "ready")
        assert pytest.wait_for(server, "ready")

        client.push(Connect(server.host, server.port))
        assert pytest.wait_for(client, "connected")
        assert pytest.wait_for(server, "connected")
        assert pytest.wait_for(client, "data", b"Ready")

        assert server.client[1] == bind_port

        client.push(Write(b"foo"))
        assert pytest.wait_for(server, "data", b"foo")

        client.push(Close())
        assert pytest.wait_for(client, "disconnected")
        assert pytest.wait_for(server, "disconnected")

        server.push(Close())
        assert pytest.wait_for(server, "closed")
    finally:
        m.stop()
