#!/usr/bin/env python

import pytest

from circuits import Manager
from circuits.core import pollers
from circuits.net.sockets import Pipe
from circuits.net.sockets import Close, Write

from client import Client

def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"Poller": pollers.Select})
    if pollers.HAS_POLL:
        metafunc.addcall(funcargs={"Poller": pollers.Poll})
    if pollers.HAS_EPOLL:
        metafunc.addcall(funcargs={"Poller": pollers.EPoll})

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

        a.push(Write("foo"))
        assert pytest.wait_for(b, "data", "foo")

        b.push(Write("foo"))
        assert pytest.wait_for(a, "data", "foo")

        a.push(Close())
        assert pytest.wait_for(a, "disconnected")

        b.push(Close())
        assert pytest.wait_for(b, "disconnected")
    finally:
        m.stop()
