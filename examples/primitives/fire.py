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
        print("Foo!")

    def bar(self):
        print("Bar!")

    def hello(self):
        self.fire(Foo())
        self.fire(Bar())
        print("Hello World!")

    def started(self, component):
        self.fire(Hello())
        self.stop()

App().run()
