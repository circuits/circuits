#!/usr/bin/env python
from circuits import Component, Event, handler


class foo(Event):

    """foo Event"""


class test(Event):

    """test Event"""


class A(Component):

    channel = "a"

    def test(self):
        return "Hello World!"

    @handler(priority=1.0)
    def _on_event(self, event, *args, **kwargs):
        return "Foo"


class B(Component):

    @handler(priority=10.0, channel="*")
    def _on_channel(self, event, *args, **kwargs):
        return "Bar"


def test_main():
    app = A() + B()
    while len(app):
        app.flush()

    x = app.fire(test(), "a")
    while len(app):
        app.flush()

    assert x.value[0] == "Bar"
    assert x.value[1] == "Foo"
    assert x.value[2] == "Hello World!"


def test_event():
    app = A() + B()
    while len(app):
        app.flush()

    e = test()
    x = app.fire(e)
    while len(app):
        app.flush()

    assert x.value[0] == "Bar"
    assert x.value[1] == "Foo"
    assert x.value[2] == "Hello World!"


def test_channel():
    app = A() + B()
    while len(app):
        app.flush()

    e = foo()
    x = app.fire(e, "b")
    while len(app):
        app.flush()

    assert x.value == "Bar"
