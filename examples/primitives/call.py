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
        x = yield self.call(foo())
        y = yield self.call(bar())
        yield x.value + y.value

    def started(self, component):
        x = yield self.call(hello())
        print("{0:d}".format(x.value))
        self.stop()


App().run()
