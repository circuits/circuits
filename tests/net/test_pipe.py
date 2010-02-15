from time import sleep

from circuits.net.sockets import Pipe
from circuits.net.sockets import Close, Write
from circuits.net.pollers import Select, Poll, EPoll

from client import Client

def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"poller": Select})
    metafunc.addcall(funcargs={"poller": Poll})
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
        assert b.data == "foo"

        b.push(Write("foo"))
        sleep(1)
        assert a.data == "foo"

        a.push(Close())
        b.push(Close())
        sleep(1)
        assert a.disconnected
        assert b.disconnected
    finally:
        a.stop()
        b.stop()
