#!/usr/bin/env python
"""Multi Bridge Example

Identical to the Hello Bridge Example but with a 2nd child.
"""
from __future__ import print_function

from os import getpid

from circuits import Component, Event, ipc


class go(Event):
    """go Event"""


class hello(Event):
    """hello Event"""


class Child(Component):

    def hello(self):
        return "Hello from child with pid {0}".format(getpid())


class App(Component):

    def init(self):
        self.counter = 0
        self.child1 = Child().start(process=True, link=self)
        self.child2 = Child().start(process=True, link=self)

    def ready(self, *args):
        self.counter += 1
        if self.counter < 2:
            return
        self.fire(go())

    def go(self):
        x = yield self.call(hello())
        yield print(x)

        y = yield self.call(ipc(hello()), self.child1[1].channel)
        yield print(y)

        z = yield self.call(ipc(hello()), self.child2[1].channel)
        yield print(z)

        raise SystemExit(0)

    def hello(self):
        return "Hello from parent with pid {0}".format(getpid())


App().run()
