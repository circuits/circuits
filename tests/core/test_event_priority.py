#!/usr/bin/env python

from circuits import Component, Event


class Foo(Event):
    """Foo Event"""


class Done(Event):
    """Done Event"""


class App(Component):

    def init(self):
        self.results = []

    def foo(self, value):
        self.results.append(value)

    def done(self):
        self.stop()


def test1():
    app = App()

    # Normal Order
    [app.fire(Foo(1)), app.fire(Foo(2))]
    app.fire(Done())

    app.run()

    assert app.results == [1, 2]


def test2():
    app = App()

    # Priority Order
    [app.fire(Foo(1), priority=2), app.fire(Foo(2), priority=0)]
    app.fire(Done())

    app.run()

    assert app.results == [2, 1]
