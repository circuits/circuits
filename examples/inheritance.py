#!/usr/bin/env python

from circuits import Event, Component

class Base(Component):

    def foo(self):
        print "Base.foo"

class Foo(Base):

    def foo(self):
        print "Foo.foo"

foo = Foo()
foo.send(Event(), "foo")
