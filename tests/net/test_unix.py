#!/usr/bin/env python

import pytest

import os
import sys
import select

if sys.platform in ("win32", "cygwin"):
    pytest.skip("Test Not Applicable on Windows")

from circuits import Manager
from circuits.net.sockets import close, connect, write
from circuits.net.sockets import UNIXServer, UNIXClient
from circuits.core.pollers import Select, Poll, EPoll, KQueue

from .client import Client
from .server import Server


def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"Poller": Select})

    if hasattr(select, "poll"):
        metafunc.addcall(funcargs={"Poller": Poll})

    if hasattr(select, "epoll"):
        metafunc.addcall(funcargs={"Poller": EPoll})

    if hasattr(select, "kqueue"):
        metafunc.addcall(funcargs={"Poller": KQueue})


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

        client.fire(connect(filename))
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
        os.remove(filename)
