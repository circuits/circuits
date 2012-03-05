#!/usr/bin/env python

import pytest

from circuits import Component, Event


class Foo(Event):
    """Foo Event"""


class Foo2(Event):
    """Foo2 Event"""


class Bar(Event):
    """Bar Event"""


class BarDone(Event):
    """fired when Bar is done"""


class Test(Component):

    def foo(self):
        x = self.fire(Bar())
        self.waitEvent("bar", 30)
        return x.value

    def foo2(self):
        x = self.callEvent(Bar())
        return x.value

    def bar(self):
        self.fire(BarDone())
        return "Foobar!"

    def bar2(self):
        self.fire(BarDone())
        return


def test_wait():
    test = Test()
    test.start()

    waiter = pytest.WaitEvent(test, "bar_done")
    x = test.fire(Foo())
    waiter.wait()

    value = x.value
    assert value == "Foobar!"

    test.stop()


def test_call():
    test = Test()
    test.start()

    e = Foo2()
    waiter = pytest.WaitEvent(test, "bar_done")
    x = test.fire(e)
    waiter.wait()

    value = x.value
    assert value == "Foobar!"

    test.stop()
