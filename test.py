#!/usr/bin/env python

from circuits import handler, Component, Debugger, Event


class Foo(Event):
    """Foo Event"""


class Bar(Event):
    """Bar Event"""


class BarDone(Event):
    """fired when Bar is done"""

class Test(Component):

    @handler("started")
    def _on_started(self, *args):
        self.fire(Foo())

    def foo(self):
        self.fire(Bar())
        e = self.wait_event(BarDone)
        print e.args[0]


    def bar(self):
        self.fire(BarDone("Foobar"))

(Test() + Debugger(events=False)).run()

