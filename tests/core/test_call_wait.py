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
        print 'called test_wait'
        x = self.fire(Hello())
        yield self.wait("hello")
        print 'AFTER HELLO'
        self.fire(Bar())
        yield x

    def test_call(self):
        yield self.call(Hello())
        yield "Bar"

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
    from circuits import Debugger
    Debugger().register(test)
    test.start()

    waiter = pytest.WaitEvent(test, "bar")
    x = test.fire(TestWait())
    waiter.wait()

    value = x.value
    print 'asserting', type(x.event)
    assert value == "Hello World!"

    test.stop()

def test_call():
    test = Test()
    test.start()

    waiter = pytest.WaitEvent(test, "test_call")
    x = test.fire(TestCall())
    waiter.wait()

    value = x.value
    #assert value == "Hello World!"
    assert value == "Bar"

    test.stop()
