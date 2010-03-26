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
    app.start()

    v = app.push(Test())

    while app: pass

    g = v.value

    s = g.next()
    assert s == "Hello"

def test_yield():
    app = App()
    app.start()

    v = app.push(Hello())

    while app: pass

    g = v.value

    s = "".join(g)
    assert s == "Hello World!"
