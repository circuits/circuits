#!/usr/bin/python -i
from circuits import Component, Event, Manager, handler


class test(Event):
    """test Event."""


class App(Component):
    @handler('test')
    def test_0(self) -> int:
        return 0

    @handler('test', priority=3)
    def test_3(self) -> int:
        return 3

    @handler('test', priority=2)
    def test_2(self) -> int:
        return 2


m = Manager()
app = App()
app.register(m)

while len(m):
    m.flush()


def test_main() -> None:
    v = m.fire(test())
    while len(m):
        m.flush()
    x = list(v)
    assert x == [3, 2, 0]
