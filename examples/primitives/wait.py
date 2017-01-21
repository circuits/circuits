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
        return 1

    def bar(self):
        return 2

    def hello(self):
        x = self.fire(foo())
        yield self.wait("foo")

        y = self.fire(bar())
        yield self.wait("bar")

        yield x.value + y.value

    def started(self, component):
        x = self.fire(hello())
        yield self.wait("hello")
        print("{0:d}".format(x.value))
        self.stop()


App().run()
