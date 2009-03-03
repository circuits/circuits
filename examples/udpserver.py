#!/usr/bin/env python

from circuits.lib.sockets import UDPServer

class EchoServer(UDPServer):

    def read(self, address, data):
        print "%s: %s" % (address, data.strip())
        self.write(address, data.strip())
    
if __name__ == "__main__":
    EchoServer(8000).run()
