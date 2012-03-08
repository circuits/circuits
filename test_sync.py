#!/usr/bin/python -i

from circuits import Event, Component, Debugger


class Foo(Event):
    """Foo Event"""


class Bar(Event):
    """Bar Event"""


class Hello(Event):
    """Hello Event"""


class Test(Event):
    """Test Event"""


class App(Component):

    def foo(self):
        x = self.fire(Bar())
        self.wait("bar")
        return x

    def bar(self):
        return "Hello World!"

    def hello(self):
        yield "Hello "
        yield "World!"

    def get_x(self):
        return 1

    def get_y(self):
        return 2

    def test(self):
        x = self.call(Event.create("GetX"))
        y = self.call(Event.create("GetY"))

        return x.value + y.value

app = App() + Debugger()
app.start()
