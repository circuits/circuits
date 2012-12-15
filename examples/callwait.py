#!/usr/bin/python

from circuits import Event, Component


class App(Component):

    def foo(self):
        return 1

    def bar(self):
        return 2

    def hello(self):
        a = yield self.call(Event.create("foo"))
        b = yield self.call(Event.create("foo"))
        yield a.value + b.value

    def started(self, component):
        x = yield self.call(Event.create("hello"))
        print(x)
        self.stop()


App().run()
