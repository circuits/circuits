#!/usr/bin/env python

from socket import socket, AF_INET, AF_INET6, SOCK_STREAM, has_ipv6
import pytest

from circuits import Manager
from circuits.core.pollers import Select
from circuits.net.sockets import TCPServer, TCP6Server, TCPClient, TCP6Client
from circuits.net.sockets import Close, Connect, Write

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
    if has_ipv6:
        _pytest_generate_tests(metafunc, ipv6=True)


def test_tcp_basic(Poller, ipv6):
    from circuits import Debugger
    m = Manager() + Poller() + Debugger()

    if ipv6:
        tcp_server = TCP6Server(("::1", 0))
        tcp_client = TCP6Client()
    else:
        tcp_server = TCPServer(0)
        tcp_client = TCPClient()
    server = Server() + tcp_server
    client = Client() + tcp_client

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


def test_tcp_reconnect(Poller, ipv6):
    m = Manager() + Poller()

    if ipv6:
        tcp_server = TCP6Server(("::1", 0))
        tcp_client = TCP6Client()
    else:
        tcp_server = TCPServer(0)
        tcp_client = TCPClient()
    server = Server() + tcp_server
    client = Client() + tcp_client

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


def test_tcp_connect_closed_port(Poller, ipv6):
    ### FIXME: This test is wrong.
    ### We need to figure out the sequence of events on Windows
    ### for this scenario. I think if you attempt to connect to
    ### a shutdown listening socket (tcp server) you should get
    ### an error event as response.

    if pytest.PLATFORM == "win32":
        pytest.skip("Broken on Windows")

    m = Manager() + Poller()
    if ipv6:
        tcp_server = TCP6Server(("::1", 0))
        tcp_client = TCP6Client()
    else:
        tcp_server = TCPServer(0)
        tcp_client = TCPClient()
    server = Server() + tcp_server
    client = Client() + tcp_client

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


def test_tcp_bind(Poller, ipv6):
    m = Manager() + Poller()

    if ipv6:
        sock = socket(AF_INET6, SOCK_STREAM)
        sock.bind(("::1", 0))
        sock.listen(5)
        _, bind_port, _, _ = sock.getsockname()
        sock.close()
        server = Server() + TCP6Server(("::1", 0))
        client = Client() + TCP6Client()
    else:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind(("", 0))
        sock.listen(5)
        _, bind_port = sock.getsockname()
        sock.close()
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

        #assert server.client[1] == bind_port

        client.fire(Write(b"foo"))
        assert pytest.wait_for(server, "data", b"foo")

        client.fire(Close())
        assert pytest.wait_for(client, "disconnected")
        assert pytest.wait_for(server, "disconnected")

        server.fire(Close())
        assert pytest.wait_for(server, "closed")
    finally:
        m.stop()
