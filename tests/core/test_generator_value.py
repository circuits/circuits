#!/usr/bin/env python

from circuits import Event, Component

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

    v = app.push(Test())
    app.flush()

    g = v.value
    s = g.next()
    assert s == "Hello"

def test_yield():
    app = App()
    while app: app.flush()

    v = app.push(Hello())
    app.flush()

    g = v.value
    s = "".join(g)
    assert s == "Hello World!"
