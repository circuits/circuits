#!/usr/bin/env python

from circuits.net.sockets import UDPServer

class EchoServer(UDPServer):

    def read(self, address, data):
        self.write(address, data.strip())
    
EchoServer(8000).run()
