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
n2 = Node(("127.0.0.1", 7000)).register(a2)
a2.start(process=True)

n1.add('bar', "127.0.0.1", 7000)

e = Event.create('foo')
e.notify = True
r = Remote(e, 'bar')
r.notify = True
a1.fire(r)


import time
time.sleep(3000)