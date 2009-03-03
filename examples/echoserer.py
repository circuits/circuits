#!/usr/bin/env python

from circuits.lib.sockets import TCPServer

class EchoServer(TCPServer):

    def read(self, sock, data):
        print "%s: %s" % (sock, data.strip())
        self.write(sock, "Got: %s" % data.strip())
    
if __name__ == "__main__":
    EchoServer(8000).run()
