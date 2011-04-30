#!/usr/bin/env python

from circuits.core.events import Started
from circuits import handler, Component, Event


class Foo(Event):
    """Foo Event"""


class Bar(Event):
    """Bar Event"""


class BarDone(Event):
    """fired when Bar is done"""


class Test(Component):

    def foo(self):
        return self.call(Bar())

    def bar(self):
        return "Foobar!"


def test_wait():
    test = Test()
    test.start()

    x = test.fire(Foo())
    assert test.waitEvent(Foo)

    assert x.value == "Foobar!"

    test.stop()
