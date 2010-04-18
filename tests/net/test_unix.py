import os
from time import sleep

from circuits.net import pollers
from circuits.net.pollers import Select
from circuits.net.sockets import Close, Connect, Write
from circuits.net.sockets import UNIXServer, UNIXClient

from client import Client
from server import Server

def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"poller": Select})
    if pollers.HAS_POLL:
        from circuits.net.pollers import Poll
        metafunc.addcall(funcargs={"poller": Poll})
    if pollers.HAS_EPOLL:
        from circuits.net.pollers import EPoll
        metafunc.addcall(funcargs={"poller": EPoll})

def test_unix(tmpdir, poller):
    sockpath = tmpdir.ensure("test.sock")
    filename = str(sockpath)
    server = Server() + UNIXServer(filename, poller=poller)
    client = Client() + UNIXClient(poller=poller)

    server.start()
    client.start()

    try:
        client.push(Connect(filename))
        sleep(1)
        assert client.connected
        assert server.connected
        assert client.data == "Ready"

        client.push(Write("foo"))
        sleep(1)
        assert server.data == "foo"

        client.push(Close())
        server.push(Close())
        sleep(1)
        assert client.disconnected
        assert server.disconnected
    finally:
        server.stop()
        client.stop()
        os.remove(filename)
