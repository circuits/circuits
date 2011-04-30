#!/usr/bin/env python

import pytest

from circuits import handler, Component, Event


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
        return self.call(Bar())

    def bar(self):
        return "Foobar!"


def test():
    test = Test()
    test.start()

    x = test.fire(Foo())

    assert pytest.wait_for(x, "result")

    value = x.value
    assert value == "Foobar!"

    test.stop()
