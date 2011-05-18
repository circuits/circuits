#!/usr/bin/env python

import pytest

from circuits import Manager
from circuits.net.sockets import Pipe
from circuits.core.pollers import Select
from circuits.net.sockets import Close, Write

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

        a.fire(Write(b"foo"))
        assert pytest.wait_for(b, "data", b"foo")

        b.fire(Write(b"foo"))
        assert pytest.wait_for(a, "data", b"foo")

        a.fire(Close())
        assert pytest.wait_for(a, "disconnected")

        b.fire(Close())
        assert pytest.wait_for(b, "disconnected")
    finally:
        m.stop()
