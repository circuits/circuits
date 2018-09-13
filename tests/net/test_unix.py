#!/usr/bin/env python
import os
import select
import sys
import tempfile

import pytest
from pytest import fixture

from circuits import Manager
from circuits.core.pollers import EPoll, KQueue, Poll, Select
from circuits.net.sockets import UNIXClient, UNIXServer, close, connect, write

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
    poller = [Select]

    if hasattr(select, "poll"):
        poller.append(Poll)

    if hasattr(select, "epoll"):
        poller.append(EPoll)

    if hasattr(select, "kqueue"):
        poller.append(KQueue)
    metafunc.parametrize('Poller', poller)


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
