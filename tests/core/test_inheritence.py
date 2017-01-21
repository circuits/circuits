#!/usr/bin/env python
import pytest

from circuits import Component, Event, handler


class test(Event):

    """test Event"""


class Base(Component):

    def test(self):
        return "Hello World!"


class App1(Base):

    @handler("test", priority=-1)
    def test(self):
        return "Foobar"


class App2(Base):

    @handler("test", override=True)
    def test(self):
        return "Foobar"


def test_inheritence():
    app = App1()
    app.start()

    x = app.fire(test())
    assert pytest.wait_for(x, "result")
    v = x.value
    assert v == ["Hello World!", "Foobar"]

    app.stop()


def test_override():
    app = App2()
    app.start()

    x = app.fire(test())
    assert pytest.wait_for(x, "result")
    v = x.value
    assert v == "Foobar"

    app.stop()
