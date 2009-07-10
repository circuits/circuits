#!/usr/bin/python -i

from circuits.core.bridge import Bridge
from circuits.tools import  graph, inspect
from circuits import Event, Component, Debugger
from circuits.net.sockets import TCPClient, TCPServer
from circuits.net.sockets import UNIXClient, UNIXServer, Pipe

class Foo(Event): pass

class A(Component):

    def foo(self):
        print "A.foo"

class B(Component):

    def foo(self):
        print "B.foo"

### UDPServer (Default)
nodes = [("127.0.0.1", 9000)]
#b1 = Bridge(bind=8000, nodes=nodes)
#b2 = Bridge(bind=9000)

### TCPClient/TCPServer
b1 = Bridge(bind=None, nodes=nodes, transport=TCPClient)
b2 = Bridge(bind=9000, transport=TCPServer)

a = A() + b1 + Debugger()
b = B() + b2 + Debugger()
a.start()
b.start()
