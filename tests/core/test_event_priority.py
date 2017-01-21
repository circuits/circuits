#!/usr/bin/env python
from circuits import Component, Event


class foo(Event):

    """foo Event"""


class done(Event):

    """done Event"""


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
    [app.fire(foo(1)), app.fire(foo(2))]
    app.fire(done())

    app.run()

    assert app.results == [1, 2]


def test2():
    app = App()

    # Priority Order
    [app.fire(foo(1), priority=2), app.fire(foo(2), priority=0)]
    app.fire(done())

    app.run()

    assert app.results == [2, 1]
