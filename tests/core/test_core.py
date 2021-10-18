#!/usr/bin/python -i
from circuits import Component, Event, Manager


class test(Event):

    """test Event"""


class App(Component):

    async def test(self):
        return "Hello World!"

    async def unregistered(self, *args):
        return

    async def prepare_unregister(self, *args):
        return


m = Manager()
app = App()
app.register(m)

while len(app):
    app.flush()


def test_fire():
    x = m.fire(test())
    m.flush()
    assert x.value == "Hello World!"


def test_contains():
    assert App in m
    assert m not in app
