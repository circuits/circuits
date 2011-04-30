#!/usr/bin/env python

import pytest

from circuits import Component, Event


class Foo(Event):
    """Foo Event"""


class Bar(Event):
    """Bar Event"""


class BarDone(Event):
    """fired when Bar is done"""


class Test(Component):

    def test_wait_class(self):
        x = self.fire(Bar())
        self.waitEvent(Bar)
        return x.value

    def test_wait_instance(self):
        e = Bar()
        x = self.fire(e)
        self.waitEvent(e)
        return x.value

    def bar(self):
        return "Foobar!"


def test_wait_class():
    test = Test()
    from circuits import Debugger
    Debugger().register(test)
    test.run()

    x = test.fire(Foo(), "test_wait_class")

    x = test.waitEvent(Bar, 30)
    value = x.value.value
    assert value == "Foobar!"

    test.stop()


def test_wait_instance():
    test = Test()
    test.run()

    x = test.fire(Foo(), "test_wait_instance")

    x = test.waitEvent(Bar, 30)

    value = x.value.value
    assert value == "Foobar!"

    test.stop()
