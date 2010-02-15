from time import sleep

from circuits.net.sockets import Write
from circuits.net.pollers import Select, Poll, EPoll
from circuits.net.sockets import UDPServer, UDPClient

from client import Client
from server import Server

def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"poller": Select, "ports": (10000, 10001)})
    metafunc.addcall(funcargs={"poller": Poll, "ports": (10002, 10003)})
    metafunc.addcall(funcargs={"poller": EPoll, "ports": (10004, 10005)})

def test_udp(poller, ports):
    server = Server() + UDPServer(ports[0], poller=poller)
    client = Client() + UDPClient(ports[1], poller=poller, channel="client")

    server.start()
    client.start()

    try:
        client.push(Write(("127.0.0.1", ports[0]), "foo"))
        sleep(1)
        assert server.data == "foo"
    finally:
        server.stop()
        client.stop()
