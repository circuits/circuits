#!/usr/bin/env python

import pytest

from circuits import Component, Event


class TestWait(Event):
    """TestWait Event"""


class TestCall(Event):
    """TestCall Event"""


class Hello(Event):
    """Hello Event"""


class Bar(Event):
    """Bar Event"""


class Test(Component):

    def test_wait(self):
        x = self.fire(Hello())
        yield self.wait("hello")
        self.fire(Bar())
        yield x

    def test_call(self):
        yield self.call(Hello())

    def hello(self):
        return "Hello World!"


def test_simple():
    test = Test()
    test.start()

    waiter = pytest.WaitEvent(test, "hello")
    x = test.fire(Hello())
    waiter.wait()

    value = x.value
    assert value == "Hello World!"

    test.stop()


def test_wait():
    test = Test()
    test.start()

    waiter = pytest.WaitEvent(test, "bar")
    x = test.fire(TestWait())
    waiter.wait()

    value = x.value
    assert value == "Hello World!"

    test.stop()

def test_call():
    test = Test()
    test.start()

    waiter = pytest.WaitEvent(test, "test_call")
    x = test.fire(TestCall())
    waiter.wait()

    value = x.value
    assert value == "Hello World!"

    test.stop()
