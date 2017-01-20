#!/usr/bin/env python

"""Simple TCP Echo Server

This example shows how you can create a simple TCP Server (an Echo Service)
utilizing the builtin Socket Components that the circuits library ships with.
"""

from circuits import Debugger, handler
from circuits.net.sockets import TCPServer


class EchoServer(TCPServer):

    @handler("read")
    def on_read(self, sock, data):
        """Read Event Handler

        This is fired by the underlying Socket Component when there has been
        new data read from the connected client.

        ..note :: By simply returning, client/server socket components listen
                  to ValueChagned events (feedback) to determine if a handler
                  returned some data and fires a subsequent Write event with
                  the value returned.
        """

        return data

# Start and "run" the system.
# Bind to port 0.0.0.0:8000
app = EchoServer(("0.0.0.0", 8000))
Debugger().register(app)
app.run()
