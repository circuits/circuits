#!/usr/bin/env python

"""Simple TCP Echo Server

This example shows how you can create a simple TCP Server (an Echo Service)
utilizing the builtin Socket Components that the circuits library ships with.
"""

import handler
from circuits.net.sockets import TCPServer


class EchoServer(TCPServer):

    @handler("read")
    def on_read(self, sock, data):
        """Read Event Handler

        This is fired by the underlying Socket Component when there has been
        new data read from the connected client.
        """

        return data

# Start and "run" the system.
# Bind to port 0.0.0.0:8000
EchoServer(8000).run()
