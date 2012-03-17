#!/usr/bin/python

import pytest

from circuits import Event, Component


class Test(Event):
    """Test Event"""

    complete = True


class Nested(Component):

    channel = "nested"

    def init(self, app):
        self.app = app

    def test(self):
        self.app.state += 1


class App(Component):

    channel = "app"

    def init(self):
        self.state = 0

    def test(self):
        self.fire(Test(), "nested")

    def test_complete(self, e, v):
        self.state += 1


def test_state():
    from circuits import Debugger
    app = App() + Debugger()
    Nested(app).register(app)
    app.start()

    pytest.WaitEvent(app, "started").wait()

    waiter = pytest.WaitEvent(app, "test_complete")
    app.fire(Test())
    waiter.wait()

    assert app.state == 2
