#!/usr/bin/env python
from circuits import Component, Event


class hello(Event):
    """hello Event."""


class foo(Event):
    """foo Event."""


class bar(Event):
    """bar Event."""


class App(Component):
    def foo(self) -> None:
        print('Foo!')

    def bar(self) -> None:
        print('Bar!')

    def hello(self) -> None:
        self.fire(foo())
        self.fire(bar())
        print('Hello World!')

    def started(self, component) -> None:
        self.fire(hello())
        self.stop()


App().run()
