#!/usr/bin/python -i

from circuits import Event, Component

class A(Component):

    def foo(self):
        self.push(Event(), "bar")

class B(Component):

    def bar(self):
        print "bar"

x = A() | B()
x.start()
