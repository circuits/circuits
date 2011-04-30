#!/usr/bin/env python

from circuits import handler, BaseComponent, Event


class Foo(Event):
    """Foo Event"""


class Test(BaseComponent):

    n = 0

    @handler("foo")
    def _on_foo(self, event, *args, **kwargs):
        print event.handler
        if self.n < 10:
            self.n += 1
            self.fire(Foo())

from circuits import Debugger
test = Test() + Debugger()
test.fire(Foo())
test.run()
