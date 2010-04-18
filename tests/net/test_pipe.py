from time import sleep

from circuits.net import pollers
from circuits.net.sockets import Pipe
from circuits.net.pollers import Select
from circuits.net.sockets import Close, Write

from client import Client

def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"poller": Select})
    if pollers.HAS_POLL:
        from circuits.net.pollers import Poll
        metafunc.addcall(funcargs={"poller": Poll})
    if pollers.HAS_EPOLL:
        from circuits.net.pollers import EPoll
        metafunc.addcall(funcargs={"poller": EPoll})

def test_pipe(poller):
    a, b = Pipe(("client", "client",), poller=poller)
    a = Client() + a
    b = Client() + b

    a.start()
    b.start()

    try:
        a.push(Write("foo"))
        sleep(1)
        s = b.data
        assert s == "foo"

        b.push(Write("foo"))
        sleep(1)
        s = a.data
        assert s == "foo"

        a.push(Close())
        b.push(Close())
        sleep(1)
        a_disconnected = a.disconnected
        b_disconnected = b.disconnected
        assert a_disconnected
        assert b_disconnected
    finally:
        a.stop()
        b.stop()
