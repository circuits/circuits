#!/usr/bin/env python

import pytest
from pytest import fixture


import os
import sys
import tempfile
import select


from circuits import Manager
from circuits.net.sockets import close, connect, write
from circuits.net.sockets import UNIXServer, UNIXClient
from circuits.core.pollers import Select, Poll, EPoll, KQueue


from .client import Client
from .server import Server


if sys.platform in ("win32", "cygwin"):
    pytest.skip("Test Not Applicable on Windows")


@fixture
def tmpfile(request):
    tmpdir = tempfile.mkdtemp()
    filename = os.path.join(tmpdir, "test.sock")

    return filename


def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"Poller": Select})

    if hasattr(select, "poll"):
        metafunc.addcall(funcargs={"Poller": Poll})

    if hasattr(select, "epoll"):
        metafunc.addcall(funcargs={"Poller": EPoll})

    if hasattr(select, "kqueue"):
        metafunc.addcall(funcargs={"Poller": KQueue})


def test_unix(tmpfile, Poller):
    m = Manager() + Poller()

    server = Server() + UNIXServer(tmpfile)
    client = Client() + UNIXClient()

    server.register(m)
    client.register(m)

    m.start()

    try:
        assert pytest.wait_for(server, "ready")
        assert pytest.wait_for(client, "ready")

        client.fire(connect(tmpfile))
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
