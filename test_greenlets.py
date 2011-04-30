#!/usr/bin/env python

from circuits import handler, Component, Debugger, Event


class Foo(Event):
    """Foo Event"""


class Bar(Event):
    """Bar Event"""


class Test(Component):

    @handler("started")
    def _on_started(self, *args):
        self.fire(Foo())

    def foo(self):
        result = self.fire(Bar())
        print result


    def bar(self):
        return "Foobar"

(Test() + Debugger(events=False)).run()
