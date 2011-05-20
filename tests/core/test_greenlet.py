#!/usr/bin/env python

import pytest
pytest.importorskip("greenlet")

from circuits import Component, Event


class Foo(Event):
    """Foo Event"""

class Foo2(Event):
    """Foo2 Event"""

class Foo3(Event):
    """Foo3 Event"""

class Foo4(Event):
    """Foo4 Event"""

class Bar(Event):
    """Bar Event"""

class Bar2(Event):
    """Bar Event"""


class BarDone(Event):
    """fired when Bar is done"""


class Test(Component):

    def foo(self):
        x = self.fire(Bar())
        self.waitEvent(Bar, 30)
        return x.value

    def foo2(self):
        e = Bar()
        x = self.fire(e)
        self.waitEvent(e, 30)
        return x.value

    def foo3(self):
        e = Bar()
        x = self.callEvent(e)
        return x.value

    def foo4(self):
        e = Bar2()
        x = self.callEvent(e)
        return x.value

    def bar(self):
        self.fire(BarDone())
        return "Foobar!"

    def bar2(self):
        self.fire(BarDone())
        return


def test_wait_class():
    test = Test()
    test.start()

    x = test.fire(Foo())
    pytest.wait_event(test, "bardone")

    value = x.value
    assert value == "Foobar!"

    test.stop()


def test_wait_instance():
    test = Test()
    test.start()

    e = Foo2()
    x = test.fire(e)
    pytest.wait_event(test, "bardone")

    value = x.value
    assert value == "Foobar!"

    test.stop()


def test_call_event():
    test = Test()
    test.start()

    e = Foo3()
    x = test.fire(e)
    pytest.wait_event(test, "bardone")

    value = x.value
    assert value == "Foobar!"

    e = Foo4()
    x = test.fire(e)
    pytest.wait_event(test, "bardone")

    value = x.value
    assert value == None

    test.stop()

