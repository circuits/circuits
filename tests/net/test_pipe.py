#!/usr/bin/env python

import pytest
if pytest.PLATFORM == "win32":
    pytest.skip("Unsupported Platform")

from circuits import Manager
from circuits.net.sockets import Pipe
from circuits.core.pollers import Select
from circuits.net.events import close, write

from .client import Client


def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"Poller": Select})


def test_pipe(Poller):
    m = Manager() + Poller()

    a, b = Pipe("a", "b")
    a.register(m)
    b.register(m)

    a = Client(channel=a.channel).register(m)
    b = Client(channel=b.channel).register(m)

    m.start()

    try:
        assert pytest.wait_for(a, "ready")
        assert pytest.wait_for(b, "ready")

        a.fire(write(b"foo"))
        assert pytest.wait_for(b, "data", b"foo")

        b.fire(write(b"foo"))
        assert pytest.wait_for(a, "data", b"foo")

        a.fire(close())
        assert pytest.wait_for(a, "disconnected")

        b.fire(close())
        assert pytest.wait_for(b, "disconnected")
    finally:
        m.stop()
