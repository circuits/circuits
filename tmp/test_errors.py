#!/usr/bin/env python

from circuits import Event, Component, Debugger

class Foo(Event): pass

class Test(Component):

    def foo(self):
        return x

test = (Test() + Debugger())

test.push(Foo())
test.send(Foo())

test.run()
