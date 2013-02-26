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
        x = self.fire(Foo())
        yield self.wait("foo")

        y = self.fire(Bar())
        yield self.wait("bar")

        yield x.value + y.value

    def started(self, component):
        x = self.fire(Hello())
        yield self.wait("hello")
        print("{0:d}".format(x.value))
        self.stop()

App().run()
