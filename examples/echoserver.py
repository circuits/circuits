#!/usr/bin/env python

from circuits.net.sockets import TCPServer, Write

class EchoServer(TCPServer):

    def read(self, sock, data):
        self.push(Write(sock, data))
    
EchoServer(8000).run()
