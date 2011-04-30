#!/usr/bin/env python

import pytest

from circuits import Component, Event


class Foo(Event):
    """Foo Event"""


class Bar(Event):
    """Bar Event"""


class FooDone(Event):
    """fire when Foo is done"""


class BarDone(Event):
    """fired when Bar is done"""


class Test(Component):

    def test_wait_class(self):
        self.fire(Bar())

    def test_wait_instance(self):
        return "Foobar!"

    def test_wait_component(self):
        e = Bar()
        event = self.fire(e)
        self.waitEvent(e)
        print("=>", id(event), repr(event))
        self.fire(FooDone())
        print(repr(event.value))
        return event.value

    def bar(self):
        return "Foobar!"


def test_wait_class():
    test = Test()
    from circuits import Debugger
    Debugger().register(test)
    test.run()

    test.fire(Foo(), "test_wait_class")
    x = test.waitEvent(Bar, 30)

    value = x.value.value
    assert value == "Foobar!"

    test.stop()


def test_wait_instance():
    test = Test()
    test.run()

    e = Foo()
    test.fire(e, "test_wait_instance")
    x = test.waitEvent(e, 30)

    value = x.value.value
    assert value == "Foobar!"

    test.stop()

def test_wait_component():
    test = Test()
    from circuits import Debugger
    Debugger().register(test)
    test.run()

    e = Foo()
    x = test.fire(e, "test_wait_component")
    test.waitEvent(FooDone, 30)
    
    print(repr(x))
    value = x.value
    assert value == "Foobar!"

    