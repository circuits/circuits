#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Echo Server

A simple Echo Server example that sends back to connected clients
the input the server receieves.

This example demonstrates:
    * Basic Component creation.
    * Basic Event handling.
    * Basic TCP Server

This example makes use of:
    * Component
    * Event
    * Manager
    * lib.sockets.TCPServer
"""

from circuits.lib.sockets import TCPServer

###
### Components
###

class EchoServer(TCPServer):

    def read(self, sock, data):
        self.write(sock, data)
    
###
### Main
###

def main():
    server = EchoServer(8000)

    while True:
        try:
            server.flush()
            server.poll()
        except KeyboardInterrupt:
            break

###
### Entry Point
###

if __name__ == "__main__":
    main()
