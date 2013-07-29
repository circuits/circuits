#!/usr/bin/env python

"""Simple Timers

A trivial simple example of using circuits and timers.
"""

from circuits import Event, Component, Timer


class App(Component):

    def hello(self):
        print("Hello World")

    def foo(self):
        print("Foo")

    def bar(self):
        print("Bar")

    def started(self, component):
        Timer(5, Event.create("Hello")).register(self)
        Timer(1, Event.create("Foo"), persist=True).register(self)
        Timer(3, Event.create("Bar"), persist=True).register(self)


App().run()
