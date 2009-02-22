# Module:   sockets
# Date:     26th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Sockets Test Suite

Test all functionality of the sockets module.
"""

import unittest
from time import sleep

from circuits import Component
from circuits.workers import Thread
from circuits.lib.sockets import TCPServer, TCPClient, UDPServer, UDPClient

class Manager(Thread):

    client = None
    server = None
    events = 0

    def run(self):
        while self.running:
            self.flush()
            self.server.poll()
            self.client.poll()

class Client(Component):

    channel = "client"

    connected = False
    disconnected = False
    error = None
    data = ""

    def connected(self, host, port):
        self.connected = True

    def disconnected(self):
        self.disconnected = True

    def read(self, data):
        self.data = data

    def error(self, error):
        self.error = error

class Server(Component):

    channel = "server"

    data = ""
    errors = {}
    server = None

    def connected(self, sock, host, port):
        self.server.write(sock, "Ready")

    def read(self, sock, data):
        self.data = data

    def error(self, sock, error):
        self.errors[sock] = error

class SocketsTestCase(unittest.TestCase):

    def testTCPClientServer(self):
        """Test sockets.TCPClient and sockets.TCPServer

        Test that communication between a TCPClient and
        TCPServer work correctly.
        """

        manager = Manager()
        tcpserver = TCPServer(9999, channel="server")
        tcpclient = TCPClient(channel="client")
        server = Server()
        client = Client()
        manager += tcpserver
        manager += tcpclient
        manager += server
        manager += client
        manager.server = tcpserver
        server.server = tcpserver
        manager.client = tcpclient

        manager.start()

        try:
            tcpclient.open("localhost", 9999)
            sleep(0.1)
            self.assertTrue(client.connected)

            self.assertTrue(client.data == "Ready")

            tcpclient.write("foo")
            sleep(0.1)
            self.assertTrue(server.data == "foo")

            tcpclient.close()
            sleep(0.1)
            self.assertTrue(client.disconnected)
        finally:
            manager.stop()
            manager.join()

    def testUDPClientServer(self):
        """Test sockets.UDPClient and sockets.UDPServer

        Test that communication between a UDPClient and
        UDPServer work correctly.
        """

        manager = Manager()
        udpserver = UDPServer(9999, channel="server")
        udpclient = UDPClient(10000, channel="client")
        server = Server()
        client = Client()
        manager += udpserver
        manager += udpclient
        manager += server
        manager += client
        manager.server = udpserver
        server.server = udpserver
        manager.client = udpclient

        manager.start()

        try:
            udpclient.connected = True
            #udpclient.open("localhost", 9999)
            #sleep(0.1)
            #self.assertTrue(client.connected)

            udpclient.write(("localhost", 9999), "foo")
            sleep(0.1)
            self.assertTrue(server.data == "foo")
        finally:
            manager.stop()
            manager.join()


def suite():
    return unittest.makeSuite(SocketsTestCase, "test")

if __name__ == "__main__":
    unittest.main()
