#!/usr/bin/env python

from circuits import Component, Event


class Hello(Event):
    """Hello Event"""


class Foo(Event):
    """Foo Event"""


class Bar(Event):
    """Bar Event"""


class App(Component):

    def foo(self):
        return 1

    def bar(self):
        return 2

    def hello(self):
        x = yield self.call(Foo())
        y = yield self.call(Bar())
        yield x.value + y.value

    def started(self, component):
        x = yield self.call(Hello())
        print("{0:d}".format(x.value))
        self.stop()

App().run()
