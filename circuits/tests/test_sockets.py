# Module:   sockets
# Date:     26th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Sockets Test Suite

Test all functionality of the sockets module.
"""

import unittest

from circuits import Component
from circuits.lib.sockets import TCPServer, TCPClient, UDPServer, UDPClient

def wait():
    for x in xrange(100000):
        pass

class Client(Component):

    def __init__(self, client):
        super(Client, self).__init__()

        self.client = client
        self.manager += self.client

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

    def __init__(self, server):
        super(Server, self).__init__()

        self.server = server
        self.manager += self.server

        self.data = ""

    def connected(self, sock, host, port):
        self.server.write(sock, "Ready")

    def read(self, sock, data):
        self.data = data

class SocketsTestCase(unittest.TestCase):

    def testTCPClientServer(self):
        """Test sockets.TCPClient and sockets.TCPServer

        Test that communication between a TCPClient and
        TCPServer work correctly.
        """

        server = Server(TCPServer(9999))
        client = Client(TCPClient("localhost", 9999))

        server.start()
        client.start()

        try:
            client.client.connect()
            wait()

            self.assertTrue(client.connected)
            self.assertTrue(client.data == "Ready")

            client.client.write("foo")
            wait()

            self.assertTrue(server.data == "foo")

            client.client.close()
            wait()

            self.assertTrue(client.disconnected)
        finally:
            server.stop()
            client.stop()

    def testUDPClientServer(self):
        """Test sockets.UDPClient and sockets.UDPServer

        Test that communication between a UDPClient and
        UDPServer work correctly.
        """

        server = Server(UDPServer(9999))
        client = Client(UDPClient(10000))

        server.start()
        client.start()

        try:
            client.client.write(("localhost", 9999), "foo")
            wait()

            self.assertTrue(server.data == "foo")
        finally:
            server.stop()
            client.stop()


def suite():
    return unittest.makeSuite(SocketsTestCase, "test")

if __name__ == "__main__":
    unittest.main()
