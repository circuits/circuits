#!/usr/bin/env python

import os
import sys

import pytest

if sys.platform in ("win32", "cygwin"):
    pytest.skip("Test Not Applicable on Windows")

from circuits import Manager
from circuits.core import pollers
from circuits.net.sockets import Close, Connect, Write
from circuits.net.sockets import UNIXServer, UNIXClient

from .client import Client
from .server import Server

def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"Poller": pollers.Select})
    if pollers.HAS_POLL:
        metafunc.addcall(funcargs={"Poller": pollers.Poll})
    if pollers.HAS_EPOLL:
        metafunc.addcall(funcargs={"Poller": pollers.EPoll})
    if pollers.HAS_KQUEUE:
        metafunc.addcall(funcargs={"Poller": pollers.KQueue})

def test_unix(tmpdir, Poller):
    m = Manager() + Poller()

    sockpath = tmpdir.ensure("test.sock")
    filename = str(sockpath)

    server = Server() + UNIXServer(filename)
    client = Client() + UNIXClient()

    server.register(m)
    client.register(m)

    m.start()

    try:
        assert pytest.wait_for(server, "ready")
        assert pytest.wait_for(client, "ready")

        client.push(Connect(filename))
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
        os.remove(filename)
