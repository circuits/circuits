#!/usr/bin/env python

from circuits import Component, Event

class Test(Event):
    """Test Event"""

class Foo(Event):
    """Foo Event"""

class Bar(Event):
    """Bar Event"""

class App(Component):

    def foo(self):
        return 1

    def bar(self):
        return 2

    def test(self):
        a = self.fire(Foo())
        b = self.fire(Bar())
        return a.value + b.value

from circuits import Debugger
app = App() + Debugger()
app.start()
