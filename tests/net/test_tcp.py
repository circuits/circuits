#!/usr/bin/env python
import os.path
import select
from socket import (
    AF_INET, AF_INET6, EAI_NODATA, EAI_NONAME, SOCK_STREAM,
    error as SocketError, has_ipv6, socket,
)
from ssl import wrap_socket as sslsocket

import pytest
from tests.conftest import WaitEvent

from circuits import Debugger, Manager
from circuits.core.pollers import EPoll, KQueue, Poll, Select
from circuits.net.events import close, connect, write
from circuits.net.sockets import TCP6Client, TCP6Server, TCPClient, TCPServer

from .client import Client
from .server import Server

CERT_FILE = os.path.join(os.path.dirname(__file__), "cert.pem")


class TestClient(object):

    def __init__(self, ipv6=False):
        self._sockname = None

        self.sock = socket(
            AF_INET6 if ipv6
            else AF_INET,
            SOCK_STREAM
        )

        self.ssock = sslsocket(self.sock)

    @property
    def sockname(self):
        return self._sockname

    def connect(self, host, port):
        self.ssock.connect_ex((host, port))
        self._sockname = self.ssock.getsockname()

    def send(self, data):
        self.ssock.send(data)

    def recv(self, buflen=4069):
        return self.ssock.recv(buflen)

    def disconnect(self):
        try:
            self.ssock.shutdown(2)
        except SocketError:
            pass

        try:
            self.ssock.close()
        except SocketError:
            pass


@pytest.fixture
def client(request, ipv6):
    client = TestClient(ipv6=ipv6)

    def finalizer():
        client.disconnect()

    request.addfinalizer(finalizer)

    return client


def wait_host(server):
    def checker(obj, attr):
        return all((getattr(obj, a) for a in attr))
    assert pytest.wait_for(server, ("host", "port"), checker)


def pytest_generate_tests(metafunc):
    ipv6 = [False]
    if has_ipv6:
        ipv6.append(True)

    for ipv6 in ipv6:
        poller = [(Select, ipv6)]

        if hasattr(select, "poll"):
            poller.append((Poll, ipv6))

        if hasattr(select, "epoll"):
            poller.append((EPoll, ipv6))

        if hasattr(select, "kqueue"):
            poller.append((KQueue, ipv6))

    metafunc.parametrize('Poller,ipv6', poller)


def test_tcp_basic(Poller, ipv6):
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

        client.fire(connect(server.host, server.port))
        assert pytest.wait_for(client, "connected")
        assert pytest.wait_for(server, "connected")
        assert pytest.wait_for(client, "data", b"Ready")

        client.fire(write(b"foo"))
        assert pytest.wait_for(server, "data", b"foo")
        assert pytest.wait_for(client, "data", b"foo")

        client.fire(close())
        assert pytest.wait_for(client, "disconnected")
        assert pytest.wait_for(server, "disconnected")

        server.fire(close())
        assert pytest.wait_for(server, "closed")
    finally:
        m.stop()


def test_tcps_basic(manager, watcher, client, Poller, ipv6):
    poller = Poller().register(manager)

    if ipv6:
        tcp_server = TCP6Server(("::1", 0), secure=True, certfile=CERT_FILE)
    else:
        tcp_server = TCPServer(0, secure=True, certfile=CERT_FILE)

    server = Server() + tcp_server

    server.register(manager)

    try:
        watcher.wait("ready", "server")

        client.connect(server.host, server.port)
        assert watcher.wait("connect", "server")
        assert client.recv() == b"Ready"

        client.send(b"foo")
        assert watcher.wait("read", "server")
        assert client.recv() == b"foo"

        client.disconnect()
        assert watcher.wait("disconnect", "server")

        server.fire(close())
        assert watcher.wait("closed", "server")
    finally:
        poller.unregister()
        server.unregister()


def test_tcp_reconnect(Poller, ipv6):
    # XXX: Apparently this doesn't work on Windows either?
    # XXX: UPDATE: Apparently Broken on Windows + Python 3.2
    # TODO: Need to look into this. Find out why...

    if pytest.PLATFORM == "win32" and pytest.PYVER[:2] >= (3, 2):
        pytest.skip("Broken on Windows on Python 3.2")

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
        client.fire(connect(server.host, server.port))
        assert pytest.wait_for(client, "connected")
        assert pytest.wait_for(server, "connected")
        assert pytest.wait_for(client, "data", b"Ready")

        client.fire(write(b"foo"))
        assert pytest.wait_for(server, "data", b"foo")

        # disconnect
        client.fire(close())
        assert pytest.wait_for(client, "disconnected")

        # 2nd reconnect
        client.fire(connect(server.host, server.port))
        assert pytest.wait_for(client, "connected")
        assert pytest.wait_for(server, "connected")
        assert pytest.wait_for(client, "data", b"Ready")

        client.fire(write(b"foo"))
        assert pytest.wait_for(server, "data", b"foo")

        client.fire(close())
        assert pytest.wait_for(client, "disconnected")
        assert pytest.wait_for(server, "disconnected")

        server.fire(close())
        assert pytest.wait_for(server, "closed")
    finally:
        m.stop()


def test_tcp_connect_closed_port(Poller, ipv6):

    if pytest.PLATFORM == "win32":
        pytest.skip("Broken on Windows")

    m = Manager() + Poller() + Debugger()

    if ipv6:
        tcp_server = TCP6Server(("::1", 0))
        tcp_client = TCP6Client(connect_timeout=1)
    else:
        tcp_server = TCPServer(0)
        tcp_client = TCPClient(connect_timeout=1)
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
        client.fire(connect(host, port))
        waiter = WaitEvent(m, "unreachable", channel='client')
        assert waiter.wait()
    finally:
        server.unregister()
        client.unregister()
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

        client.fire(connect(server.host, server.port))
        assert pytest.wait_for(client, "connected")
        assert pytest.wait_for(server, "connected")
        assert pytest.wait_for(client, "data", b"Ready")

        # assert server.client[1] == bind_port

        client.fire(write(b"foo"))
        assert pytest.wait_for(server, "data", b"foo")

        client.fire(close())
        assert pytest.wait_for(client, "disconnected")
        assert pytest.wait_for(server, "disconnected")

        server.fire(close())
        assert pytest.wait_for(server, "closed")
    finally:
        m.stop()


def test_tcp_lookup_failure(manager, watcher, Poller, ipv6):
    poller = Poller().register(manager)

    if ipv6:
        tcp_client = TCP6Client()
    else:
        tcp_client = TCPClient()

    client = Client() + tcp_client
    client.register(manager)

    try:
        assert watcher.wait("ready", "client")

        client.fire(connect("foo.bar.baz", 1234))
        assert watcher.wait("error", "client")

        if pytest.PLATFORM == "win32":
            assert client.error.errno == 11004
        else:
            assert client.error.errno in (EAI_NODATA, EAI_NONAME,)
    finally:
        poller.unregister()
        client.unregister()
