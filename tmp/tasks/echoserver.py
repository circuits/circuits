#!/usr/bin/env python

from circuits import async
from circuits.lib.sockets import acceptor

@async
def echoserver():
    for sock in acceptor(port=8000):
        sock.write(sock.read())

echoserver()
