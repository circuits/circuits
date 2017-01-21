#!/usr/bin/env python
"""Bridge Example

This example is quite similar to the Hello example
but displays a hello form both the parent and child
processing demonstrating how IPC works using the Bridge.
"""
from __future__ import print_function

from os import getpid

from circuits import Component, Event, ipc


class hello(Event):
    """hello Event"""


class Child(Component):

    def hello(self):
        return "Hello from child with pid {0}".format(getpid())


class App(Component):

    def init(self):
        Child().start(process=True, link=self)

    def ready(self, *args):
        x = yield self.call(hello())
        yield print(x)

        y = yield self.call(ipc(hello()))
        yield print(y)

        raise SystemExit(0)

    def hello(self):
        return "Hello from parent with pid {0}".format(getpid())


App().run()
