#!/usr/bin/env python

from circuits.net.sockets import TCPServer

class EchoServer(TCPServer):

    def read(self, sock, data):
        self.write(sock, data)
    
EchoServer(8000).run()
