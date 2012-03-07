#!/usr/bin/env python

from circuits import Event, Component
from itertools import islice

class Test(Event):
    """Test Event"""

class Hello(Event):
    """Hello Event"""

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
    while app: app.flush()

    v = app.fire(Test())
    app.tick()
    app.tick()

    x = list(islice(v.value, 0, 2))
    assert x == ["Hello", "Hello"]

def test_yield():
    app = App()
    while app: app.flush()

    v = app.fire(Hello())
    app.tick()
    app.tick()
    app.tick()

    x = list(v.value)
    assert x == ["Hello ", "World!"]
