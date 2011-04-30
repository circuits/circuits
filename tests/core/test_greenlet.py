#!/usr/bin/env python

from circuits import Component, Event
from circuits.core.events import Started


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

    assert test.waitEvent(Started)

    test.stop()
