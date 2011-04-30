#!/usr/bin/env python

import pytest

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
        x = self.fire(Bar())
        self.waitEvent(Bar)
        return x.value

    def bar(self):
        return "Foobar!"


def test_wait():
    test = Test()
    test.start()

    x = test.fire(Foo())

    pytest.wait_for(x, "result")

    value = x.value
    assert value == "Foobar!"

    test.stop()
