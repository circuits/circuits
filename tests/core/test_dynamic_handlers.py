#!/usr/bin/env python
import pytest

from circuits import Event, Manager, handler


class foo(Event):

    """foo Event"""


@handler("foo")
def on_foo(self):
    return "Hello World!"


def test_addHandler():
    m = Manager()
    m.start()

    m.addHandler(on_foo)

    waiter = pytest.WaitEvent(m, "foo")
    x = m.fire(foo())
    waiter.wait()

    s = x.value
    assert s == "Hello World!"

    m.stop()


def test_removeHandler():
    m = Manager()
    m.start()

    method = m.addHandler(on_foo)

    waiter = pytest.WaitEvent(m, "foo")
    x = m.fire(foo())
    waiter.wait()

    s = x.value
    assert s == "Hello World!"

    m.removeHandler(method)

    waiter = pytest.WaitEvent(m, "foo")
    x = m.fire(foo())
    waiter.wait()

    assert x.value is None

    assert on_foo not in dir(m)
    assert "foo" not in m._handlers

    m.stop()
