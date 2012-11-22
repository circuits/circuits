#!/usr/bin/python -i

from circuits import Event, Component, Debugger, Manager


class A(Component):

    channel = "a"

    def foo(self):
        return "Hello"


class B(Component):

    channel = "b"

    def foo(self):
        return "World!"


class App(Component):

    def hello(self):
        a = yield self.call(Event.create("foo"), "a")
        b = yield self.call(Event.create("foo"), "b")
        yield "{0} {1}".format(a, b)

m = Manager() + Debugger()
A().register(m)
B().register(m)
App().register(m)
m.start()
