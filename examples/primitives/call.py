#!/usr/bin/env python
from circuits import Component, Event


class hello(Event):
    """hello Event."""


class foo(Event):
    """foo Event."""


class bar(Event):
    """bar Event."""


class App(Component):
    def foo(self) -> int:
        return 1

    def bar(self) -> int:
        return 2

    def hello(self):
        x = yield self.call(foo())
        y = yield self.call(bar())
        yield x.value + y.value

    def started(self, component):
        x = yield self.call(hello())
        print(f'{x.value:d}')
        self.stop()


App().run()
