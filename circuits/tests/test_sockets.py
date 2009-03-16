# Module:   sockets
# Date:     26th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Sockets Test Suite

Test all functionality of the sockets module.
"""

import unittest
from time import sleep

from circuits.tools import inspect
from circuits import Component, Debugger
from circuits.lib.sockets import *

def wait():
    sleep(0.1)

class Client(Component):

    channel = "client"

    def __init__(self):
        super(Client, self).__init__()

        self.connected = False
        self.disconnected = False
        self.data = ""

    def connected(self, host, port):
        self.connected = True

    def disconnected(self):
        self.disconnected = True

    def read(self, data):
        self.data = data

class Server(Component):

    channel = "server"

    def __init__(self):
        super(Server, self).__init__()

        self.connected = False
        self.disconnected = False
        self.data = ""

    def connect(self, sock, host, port):
        self.connected = True
        self.push(Write(sock, "Ready"), "write")

    def disconnect(self, sock):
        self.disconnected = True

    def read(self, sock, data):
        self.data = data

class SocketsTestCase(unittest.TestCase):

    def testTCPClientServer(self):
        """Test sockets.TCPClient and sockets.TCPServer

        Test that communication between a TCPClient and
        TCPServer work correctly.
        """

        server = Server() + TCPServer(9999)
        client = Client() + TCPClient()

        server.start()
        client.start()

        try:
            client.push(Connect("127.0.0.1", 9999), "connect")
            wait()

            self.assertTrue(client.connected)
            self.assertTrue(server.connected)
            self.assertTrue(client.data == "Ready")

            client.push(Write("foo"), "write")
            wait()

            self.assertTrue(server.data == "foo")

            client.push(Close(), "close")
            wait()

            self.assertTrue(client.disconnected)
            self.assertTrue(server.disconnected)
        finally:
            server.stop()
            client.stop()

    def testUDPClientServer(self):
        """Test sockets.UDPClient and sockets.UDPServer

        Test that communication between a UDPClient and
        UDPServer work correctly.
        """

        server = Server() + UDPServer(9999)
        client = Client() + UDPClient(10000, channel="client")

        server.start()
        client.start()

        try:
            client.push(Write(("127.0.0.1", 9999), "foo"), "write")
            wait()
            client.push(Write(("127.0.0.1", 9999), "foo"), "write")
            sleep(1)
            print repr(server.data)
            self.assertTrue(server.data == "foo")
        finally:
            server.stop()
            client.stop()


def suite():
    return unittest.makeSuite(SocketsTestCase, "test")

if __name__ == "__main__":
    unittest.main()
