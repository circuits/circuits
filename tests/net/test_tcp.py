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
    server = Server() + TCPServer(("127.0.0.1", port), poller=poller)
    client = Client() + TCPClient(poller=poller)

    server.start()
    client.start()

    try:
        client.push(Connect("127.0.0.1", port))
        sleep(1)
        client_connected = client.connected
        server_connected = server.connected
        s = client.data
        assert client_connected
        assert server_connected
        assert s == "Ready"

        client.push(Write("foo"))
        sleep(1)
        s = server.data
        assert s == "foo"

        client.push(Close())
        sleep(1)
        server.push(Close())
        sleep(1)
        client_disconnected = client.disconnected
        server_disconnected = server.disconnected
        assert client_disconnected
        assert server_disconnected
    finally:
        server.stop()
        client.stop()
