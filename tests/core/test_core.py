#!/usr/bin/python -i
from circuits import Component, Event, Manager


class test(Event):
    """test Event."""


class App(Component):
    def test(self) -> str:
        return 'Hello World!'

    def unregistered(self, *args) -> None:
        return

    def prepare_unregister(self, *args) -> None:
        return


m = Manager()
app = App()
app.register(m)

while len(app):
    app.flush()


def test_fire() -> None:
    x = m.fire(test())
    m.flush()
    assert x.value == 'Hello World!'


def test_contains() -> None:
    assert App in m
    assert m not in app
