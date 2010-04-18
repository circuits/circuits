from time import sleep

from circuits.net import pollers
from circuits.net.pollers import Select
from circuits.net.sockets import TCPServer, TCPClient
from circuits.net.sockets import Close, Connect, Write

from client import Client
from server import Server

def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"poller": Select, "port": 9000})
    if pollers.HAS_POLL:
        from circuits.net.pollers import Poll
        metafunc.addcall(funcargs={"poller": Poll, "port": 9001})
    if pollers.HAS_EPOLL:
        from circuits.net.pollers import EPoll
        metafunc.addcall(funcargs={"poller": EPoll, "port": 9002})

def test_tcp(poller, port):
    server = Server() + TCPServer(port, poller=poller)
    client = Client() + TCPClient(poller=poller)

    server.start()
    client.start()

    try:
        client.push(Connect("127.0.0.1", port))
        sleep(1)
        assert client.connected
        assert server.connected
        assert client.data == "Ready"

        client.push(Write("foo"))
        sleep(1)
        assert server.data == "foo"

        client.push(Close())
        sleep(1)
        server.push(Close())
        sleep(1)
        assert client.disconnected
        assert server.disconnected
    finally:
        server.stop()
        client.stop()
