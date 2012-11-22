#!/usr/bin/env python

from time import time
from socket import socket, AF_INET, SOCK_STREAM
import pytest

from circuits import Manager
from circuits.core.pollers import Select
from circuits.net.sockets import TCPServer, TCPClient
from circuits.net.sockets import Close, Connect, Write

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
        wait_host(server)

        client.fire(Connect(server.host, server.port))
        assert pytest.wait_for(client, "connected")
        assert pytest.wait_for(server, "connected")
        assert pytest.wait_for(client, "data", b"Ready")

        client.fire(Write(b"foo"))
        assert pytest.wait_for(server, "data", b"foo")
        assert pytest.wait_for(client, "data", b"foo")

        client.fire(Close())
        assert pytest.wait_for(client, "disconnected")
        assert pytest.wait_for(server, "disconnected")

        server.fire(Close())
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
        wait_host(server)

        # 1st connect
        client.fire(Connect(server.host, server.port))
        assert pytest.wait_for(client, "connected")
        assert pytest.wait_for(server, "connected")
        assert pytest.wait_for(client, "data", b"Ready")

        client.fire(Write(b"foo"))
        assert pytest.wait_for(server, "data", b"foo")

        # disconnect
        client.fire(Close())
        assert pytest.wait_for(client, "disconnected")

        # 2nd reconnect
        client.fire(Connect(server.host, server.port))
        assert pytest.wait_for(client, "connected")
        assert pytest.wait_for(server, "connected")
        assert pytest.wait_for(client, "data", b"Ready")

        client.fire(Write(b"foo"))
        assert pytest.wait_for(server, "data", b"foo")

        client.fire(Close())
        assert pytest.wait_for(client, "disconnected")
        assert pytest.wait_for(server, "disconnected")

        server.fire(Close())
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
        wait_host(server)

        host, port = server.host, server.port
        tcp_server._sock.close()

        # 1st connect
        client.fire(Connect(host, port))
        assert pytest.wait_for(client, "connected")

        client.fire(Write(b"foo"))
        assert pytest.wait_for(client, "disconnected")

        client.disconnected = False
        client.fire(Write(b"foo"))
        assert pytest.wait_for(client, "disconnected", timeout=1.0) is None
    finally:
        m.stop()


def test_tcp_bind(Poller):
    m = Manager() + Poller()

    sock = socket(AF_INET, SOCK_STREAM)
    sock.listen(0)
    _, bind_port = sock.getsockname()
    sock.close()

    server = Server() + TCPServer(0)
    client = Client() + TCPClient(bind_port)

    server.register(m)
    client.register(m)

    m.start()

    try:
        assert pytest.wait_for(client, "ready")
        assert pytest.wait_for(server, "ready")
        wait_host(server)

        client.fire(Connect(server.host, server.port))
        assert pytest.wait_for(client, "connected")
        assert pytest.wait_for(server, "connected")
        assert pytest.wait_for(client, "data", b"Ready")

        assert server.client[1] == bind_port

        client.fire(Write(b"foo"))
        assert pytest.wait_for(server, "data", b"foo")

        client.fire(Close())
        assert pytest.wait_for(client, "disconnected")
        assert pytest.wait_for(server, "disconnected")

        server.fire(Close())
        assert pytest.wait_for(server, "closed")
    finally:
        m.stop()
