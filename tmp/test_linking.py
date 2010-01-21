#!/usr/bin/python -i

from circuits.tools import  graph, inspect
from circuits import Event, Component, Manager, Debugger

class A(Component):

    channel = "a"

    def foo(self):
        print "A.foo"

class B(Component):

    channel = "b"

    def foo(self):
        print "B.foo"

m = Manager() + Debugger()
a = A()
m += a
b = B()
m += b
a.start(process=True, link=True)
m.start()
