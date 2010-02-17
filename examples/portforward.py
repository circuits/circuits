#!/usr/bin/env python

import optparse

from circuits import __version__
from circuits import Event, Component, Debugger
from circuits.net.sockets import TCPClient, TCPServer
from circuits.net.sockets import Close, Connect, Write

USAGE = "%prog [options]"
VERSION = "%prog v" + __version__

def parse_options():
    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-s", "--ssl",
            action="store_true", default=False, dest="ssl",
            help="Enable Secure Socket Layer (SSL)")

    parser.add_option("-b", "--bind",
            action="store", default=None, dest="bind",
            help="Address and port to bind to")

    parser.add_option("-t", "--target",
            action="store", default=None, dest="target",
            help="Target address and port to forward to")

    opts, args = parser.parse_args()

    if opts.bind is None:
        parser.print_help()
        raise SystemExit, 1
    
    if opts.target is None:
        parser.print_help()
        raise SystemExit, 1

    return opts, args

class ClientConnected(Event): pass
class ClientDisconnected(Event): pass
class ClientRead(Event): pass
class ClientWrite(Event): pass

class Server(TCPServer):

    channel = "server"

    def connect(self, sock, host, port):
        self.push(ClientConnected(host, port), target="client")

    def disconnect(self, sock):
        self.push(ClientDisconnected(), target="client")

    def read(self, sock, data):
        self.push(ClientRead(data), target="client")
    
    def clientwrite(self, data):
        self.broadcast(data)

class Client(TCPClient):

    channel = "client"

    def __init__(self, host, port):
        super(Client, self).__init__()

        self.host = host
        self.port = port

    def clientconnected(self, host, port):
        self.push(Connect(self.host, self.port))
    
    def clientdisconnected(self):
        self.push(Close())
    
    def clientread(self, data):
        self.push(Write(data))

    def read(self, data):
        self.push(ClientWrite(data), target="server")

def main():
    opts, args = parse_options()

    if ":" in opts.bind:
        address, port = opts.bind.split(":")
        port = int(port)
        bind = (address, port)
    else:
        bind = (opts.bind, 8000)

    if ":" in opts.target:
        address, port = opts.target.split(":")
        port = int(port)
        target = (address, port)
    else:
        target = (opts.target, 8000)

    (Server(bind) + Client(*target) + Debugger()).run()

if __name__ == "__main__":
    main()
