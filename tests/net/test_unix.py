#!/usr/bin/env python

import os
import sys

import pytest

if sys.platform in ("win32", "cygwin"):
    pytest.skip("Test Not Applicable on Windows")

from circuits import Manager
from circuits.core.pollers import Select
from circuits.net.sockets import Close, Connect, Write
from circuits.net.sockets import UNIXServer, UNIXClient

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

        client.fire(Connect(filename))
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
        os.remove(filename)
