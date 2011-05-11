#!/usr/bin/env python

import pytest
pytest.importorskip("greenlet")

from circuits import Component, Event


class Foo(Event):
    """Foo Event"""


class Bar(Event):
    """Bar Event"""

class Bar2(Event):
    """Bar Event"""


class BarDone(Event):
    """fired when Bar is done"""


class Test(Component):

    def test_wait_class(self):
        x = self.fire(Bar())
        self.waitEvent(Bar, 30)
        return x.value

    def test_wait_instance(self):
        e = Bar()
        x = self.fire(e)
        self.waitEvent(e, 30)
        return x.value

    def test_call_event(self):
        e = Bar()
        x = self.callEvent(e)
        return x.value

    def test_call_event2(self):
        e = Bar2()
        x = self.callEvent(e)
        return x.value

    def bar(self):
        self.push(BarDone())
        return "Foobar!"

    def bar2(self):
        self.push(BarDone())
        return


def test_wait_class():
    test = Test()
    test.start()

    x = test.fire(Foo(), "test_wait_class")
    pytest.wait_event(test, "bardone")

    value = x.value
    assert value == "Foobar!"

    test.stop()


def test_wait_instance():
    test = Test()
    test.start()

    e = Foo()
    x = test.fire(e, "test_wait_instance")
    pytest.wait_event(test, "bardone")

    value = x.value
    assert value == "Foobar!"

    test.stop()


def test_call_event():
    test = Test()
    test.start()

    e = Foo()
    x = test.fire(e, "test_call_event")
    pytest.wait_event(test, "bardone")

    value = x.value
    assert value == "Foobar!"

    x = test.fire(e, "test_call_event2")
    pytest.wait_event(test, "bardone")

    value = x.value
    assert value == None

    test.stop()

