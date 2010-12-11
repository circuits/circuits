#!/usr/bin/env python

import py

from circuits.core import pollers
from circuits.net.sockets import Pipe
from circuits.core.pollers import Select
from circuits.net.sockets import Close, Write

from client import Client

def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"poller": Select})
    if pollers.HAS_POLL:
        from circuits.core.pollers import Poll
        metafunc.addcall(funcargs={"poller": Poll})
    if pollers.HAS_EPOLL:
        from circuits.core.pollers import EPoll
        metafunc.addcall(funcargs={"poller": EPoll})

def test_pipe(poller):
    a, b = Pipe(("client", "client",), poller=poller)
    a = Client() + a
    b = Client() + b

    a.start()
    b.start()

    try:
        a.push(Write("foo"))
        py.test.wait_for(b, "data", "foo")

        b.push(Write("foo"))
        py.test.wait_for(a, "data", "foo")

        a.push(Close())
        b.push(Close())
        py.test.wait_for(a, "disconnected")
        py.test.wait_for(b, "disconnected")
    finally:
        a.stop()
        b.stop()
