#!/usr/bin/env python

from circuits import *
from circuits.lib.io import *
from circuits.lib.sockets import *

from fun import *

class Connection(TCPClient):

    def __init__(self, host, port):
        super(Connection, self).__init__(host, port)

        self.start()
        self.push(Connect(), "connect")

@task
def forwarder(source, target): # Problem here
    for line in source:
        target.write(line)

socket = Connection("localhost", 8000)
socket += Debugger()

stdin += Debugger()
stdout += Debugger()

forwarder(stdin, socket)
forwarder(socket, stdout)

# Problem here -something- needs to run!

stdin.start()
stdout.start()
socket.start()

scheduler.run() # Do we run the scheduler ?
