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
        yield self.wait("bar")
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

    waiter = pytest.WaitEvent(test, "hello_success")
    x = test.fire(TestWait())
    waiter.wait()

    value = x.value
    assert value == "Hello World!"

    test.stop()


def test_call():
    test = Test()
    test.start()

    waiter = pytest.WaitEvent(test, "hello_success")
    x = test.fire(TestCall())
    waiter.wait()

    value = x.value
    assert value == "Hello World!"

    test.stop()


def test_long_call():
    test = Test()
    from circuits import Debugger
    Debugger().register(test)
    test.start()

    waiter = pytest.WaitEvent(test, "test_long_call")
    x = test.fire(TestLongCall())
    waiter.wait()

    value = x.value
    assert value == range(1, 10)

    test.stop()


def test_long_wait():
    test = Test()
    from circuits import Debugger
    Debugger().register(test)
    test.start()

    waiter = pytest.WaitEvent(test, "test_long_wait")
    x = test.fire(TestLongWait())
    waiter.wait()

    value = x.value
    assert value == range(1, 10)

    test.stop()
