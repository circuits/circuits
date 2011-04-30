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
    test.start()

    x = test.fire(Foo(), "test_wait_class")

    pytest.wait_for(x, "result")

    value = x.value
    assert value == "Foobar!"

    test.stop()


def test_wait_instance():
    test = Test()
    test.start()

    x = test.fire(Foo(), "test_wait_instance")

    pytest.wait_for(x, "result")

    value = x.value
    assert value == "Foobar!"

    test.stop()
