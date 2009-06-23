#!/usr/bin/python -i

from circuits import Event, Component, Debugger, Manager

class Foo(Component):

    def foo(self):
        return "foo"

m = Manager() + Foo() + Debugger()
m.start()
