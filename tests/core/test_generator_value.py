#!/usr/bin/env python
from circuits import Component, Event


class test(Event):

    """test Event"""


class hello(Event):

    """hello Event"""


class App(Component):

    def test(self):
        def f():
            while True:
                yield "Hello"
        return f()

    def hello(self):
        yield "Hello "
        yield "World!"


def test_return_generator():
    app = App()
    while len(app):
        app.flush()

    v = app.fire(test())
    app.tick()
    app.tick()

    x = v.value
    assert x == "Hello"


def test_yield():
    app = App()
    while len(app):
        app.flush()

    v = app.fire(hello())
    app.tick()
    app.tick()
    app.tick()

    x = v.value
    assert x == ["Hello ", "World!"]
