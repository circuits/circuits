#!/usr/bin/env python

from circuits.node import Node, Remote
from circuits import Component, Debugger, Event


class Foo(Event):
    """Foo Event"""


class App(Component):

    def foo(self):
        return "Hello World!"

a1 = App() + Debugger()
n1 = Node().register(a1)
a1.start()

a2 = App() + Debugger()
n2 = Node(7000).register(a2)
a2.start(process=True)
