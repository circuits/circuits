# Module:   sockets
# Date:     26th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Sockets Test Suite"""

import unittest
from time import sleep

from circuits import Component
from circuits.net.sockets import *

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


class TestCloseEvent(unittest.TestCase):
    """Test Close Event"""

    def runTest(self):
        # Client Mode
        e = Close()
        self.assertFalse(e.args)

        # Server Mode
        e = Close(1)
        self.assertEquals(e.args[0], 1)

class TestConnectEvent(unittest.TestCase):
    """Test Connect Event"""

    def runTest(self):
        # Client Mode (host, port, ssl=False)
        e = Connect("localhost", 1234, ssl=True)
        self.assertEquals(e[0], "localhost")
        self.assertEquals(e[1], 1234)
        self.assertEquals(e["ssl"], True)

        e = Connect("localhost", 1234, ssl=False)
        self.assertEquals(e[0], "localhost")
        self.assertEquals(e[1], 1234)
        self.assertEquals(e["ssl"], False)

        # Server Mode (sock, host, port)
        e = Connect(1, "localhost", 1234)
        self.assertEquals(e[0], 1)
        self.assertEquals(e[1], "localhost")
        self.assertEquals(e[2], 1234)

class TestConnectedEvent(unittest.TestCase):
    """Test Connected Event"""

    def runTest(self):
        e = Connected("localhost", 1234)
        self.assertEquals(e[0], "localhost")
        self.assertEquals(e[1], 1234)

class TestDisconnectEvent(unittest.TestCase):
    """Test Disconnect Event"""

    def runTest(self):
        # Client Mode
        e = Disconnect()
        self.assertFalse(e.args)

        # Server Mode
        e = Disconnect(1)
        self.assertEquals(e.args[0], 1)

class TestDisconnectedEvent(unittest.TestCase):
    """Test Disconnected Event"""

    def runTest(self):
        e = Disconnected()
        self.assertFalse(e.args)

class TestErrorEvent(unittest.TestCase):
    """Test Error Event"""

    def runTest(self):
        # Client Mode
        e = Error("error")
        self.assertEquals(e[0], "error")

        # Server Mode
        e = Error(1, "error")
        self.assertEquals(e[0], 1)
        self.assertEquals(e[1], "error")

class TestReadEvent(unittest.TestCase):
    """Test Read Event"""

    def runTest(self):
        # Client Mode
        e = Read("data")
        self.assertEquals(e[0], "data")

        # Server Mode
        e = Read(1, "data")
        self.assertEquals(e[0], 1)
        self.assertEquals(e[1], "data")

class TestWriteEvent(unittest.TestCase):
    """Test Write Event"""

    def runTest(self):
        # Client Mode
        e = Write("data")
        self.assertEquals(e[0], "data")

        # Server Mode
        e = Write(1, "data")
        self.assertEquals(e[0], 1)
        self.assertEquals(e[1], "data")

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
            self.assertTrue(server.data == "foo")
        finally:
            server.stop()
            client.stop()


def suite():
    return unittest.makeSuite(SocketsTestCase, "test")

if __name__ == "__main__":
    unittest.main()
