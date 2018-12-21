#!/usr/bin/python -i
import pytest

from circuits import BaseComponent, Component, Event, Manager, handler


class test(Event):

    """test Event"""


class App(Component):

    @handler("test")
    def test_0(self):
        return 0

    @handler("test", priority=3)
    def test_3(self):
        return 3

    @handler("test", priority=2)
    def test_2(self):
        return 2


def test_main():
    m = Manager()
    app = App()
    app.register(m)

    while len(m):
        m.flush()

    v = m.fire(test())
    while len(m):
        m.flush()
    x = list(v)
    assert x == [3, 2, 0]


class App2(BaseComponent):

    @handler('test', priority=3)
    def _on_test3(self, event):
        return 3

    @handler('test', priority=2)
    def _on_test2(self, event):
        event.stop()
        yield
        yield 2

    @handler('test', priority=1)
    def _on_test1(self, event):
        return 1


@pytest.mark.xfail(reason='')
def test_coroutine():
    m = Manager()
    app = App2()
    app.register(m)

    while len(m):
        m.flush()

    v = m.fire(test())
    while len(m):
        m.flush()
    x = list(v)
    assert x == [3, 2]
