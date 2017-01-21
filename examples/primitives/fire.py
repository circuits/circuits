#!/usr/bin/env python
from circuits import Component, Event


class hello(Event):

    """hello Event"""


class foo(Event):

    """foo Event"""


class bar(Event):

    """bar Event"""


class App(Component):

    def foo(self):
        print("Foo!")

    def bar(self):
        print("Bar!")

    def hello(self):
        self.fire(foo())
        self.fire(bar())
        print("Hello World!")

    def started(self, component):
        self.fire(hello())
        self.stop()


App().run()
