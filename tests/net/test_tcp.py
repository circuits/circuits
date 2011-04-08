#!/usr/bin/env python

import pytest

from circuits import Manager
from circuits.core import pollers
from circuits.net.sockets import TCPServer, TCPClient
from circuits.net.sockets import Close, Connect, Write

from client import Client
from server import Server

def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"Poller": pollers.Select})
    if pollers.HAS_POLL:
        metafunc.addcall(funcargs={"Poller": pollers.Poll})
    if pollers.HAS_EPOLL:
        metafunc.addcall(funcargs={"Poller": pollers.EPoll})
    if pollers.HAS_KQUEUE:
        metafunc.addcall(funcargs={"Poller": pollers.KQueue})

def test_tcp(Poller):
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
        assert pytest.wait_for(client, "data", "Ready")

        client.push(Write("foo"))
        assert pytest.wait_for(server, "data", "foo")

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
        assert pytest.wait_for(client, "data", "Ready")

        client.push(Write("foo"))
        assert pytest.wait_for(server, "data", "foo")

        # disconnect
        client.push(Close())
        assert pytest.wait_for(client, "disconnected")

        # 2nd reconnect
        client.push(Connect(server.host, server.port))
        assert pytest.wait_for(client, "connected")
        assert pytest.wait_for(server, "connected")
        assert pytest.wait_for(client, "data", "Ready")

        client.push(Write("foo"))
        assert pytest.wait_for(server, "data", "foo")

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
        server.push(Close())
        assert pytest.wait_for(server, "closed")
        tcp_server._sock.close()

        # 1st connect
        client.push(Connect(host, port))
        assert pytest.wait_for(client, "connected")

        client.push(Write("foo"))
        assert pytest.wait_for(client, "disconnected")
    finally:
        m.stop()
    