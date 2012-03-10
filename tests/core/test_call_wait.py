#!/usr/bin/env python

import pytest

from circuits import Component, Event


class TestWait(Event):
    """TestWait Event"""


class TestCall(Event):
    """TestCall Event"""


class TestLongCall(Event):
    """TestLongCall Event"""


class TestLongWait(Event):
    """TestLongCall Event"""


class Hello(Event):
    """Hello Event"""

    success = True


class Foo(Event):
    """Foo Event"""


class Test(Component):

    def test_wait(self):
        x = self.fire(Hello())
        yield self.wait("hello")
        yield x

    def test_call(self):
        yield self.call(Hello())

    def hello(self):
        return "Hello World!"

    def test_long_wait(self):
        x = self.fire(Foo())
        yield self.wait("foo")
        yield x.value

    def test_long_call(self):
        yield self.call(Foo())

    def foo(self):
        for i in xrange(1, 10):
            yield i


def test_wait():
    test = Test()
    test.start()

    x = pytest.call_event_from_name(test, TestWait(), "hello_success")
    value = x.value
    assert value == "Hello World!"

    test.stop()


def test_call():
    test = Test()
    test.start()

    x = pytest.call_event(test, TestCall())
    value = x.value
    assert value == "Hello World!"

    test.stop()


def test_long_call():
    test = Test()
    test.start()

    x = pytest.call_event(test, TestLongCall())

    value = x.value
    assert value == range(1, 10)

    test.stop()


def test_long_wait():
    test = Test()
    test.start()

    x = pytest.call_event(test, TestLongWait())

    value = x.value
    assert value == range(1, 10)

    test.stop()
