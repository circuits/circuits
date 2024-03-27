#!/usr/bin/env python
from circuits import Component, Event


class foo(Event):
    """foo Event."""


class done(Event):
    """done Event."""


class App(Component):
    def init(self) -> None:
        self.results = []

    def foo(self, value) -> None:
        self.results.append(value)

    def done(self) -> None:
        self.stop()


def test1() -> None:
    app = App()

    # Normal Order
    [app.fire(foo(1)), app.fire(foo(2))]
    app.fire(done())

    app.run()

    assert app.results == [1, 2]


def test2() -> None:
    app = App()

    # Priority Order
    [app.fire(foo(1), priority=2), app.fire(foo(2), priority=0)]
    app.fire(done())

    app.run()

    assert app.results == [2, 1]
