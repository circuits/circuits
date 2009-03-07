#!/usr/bin/env python

from circuits.lib.sockets import TCPServer

class EchoServer(TCPServer):

    def read(self, sock, data):
        self.write(sock, data)
    
if __name__ == "__main__":
    EchoServer(8000).run()
