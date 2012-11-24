#!/usr/bin/env python

import pytest
pytest.skip("XXX: This test hangs")

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


class GetX(Event):
    """Get X Event"""


class GetY(Event):
    """Get Y Event"""


class TestEval(Event):
    """Test Eval Event"""


class Test(Component):

    def test_wait(self):
        x = self.fire(Hello())
        yield self.wait("hello")
        yield x

    def test_call(self):
        x = yield self.call(Hello())
        yield x

    def hello(self):
        return "Hello World!"

    def test_long_wait(self):
        x = self.fire(Foo())
        yield self.wait("foo")
        yield x

    def test_long_call(self):
        x = yield self.call(Foo())
        yield x

    def foo(self):
        for i in xrange(1, 10):
            yield i

    def get_x(self):
        return 1

    def get_y(self):
        return 2

    def test_eval(self):
        x = yield self.call(GetX())
        y = yield self.call(GetY())
        yield x.value + y.value


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


def test_eval():
    test = Test()
    test.start()

    x = pytest.call_event(test, TestEval())
    value = x.value
    assert value == 3

    test.stop()
