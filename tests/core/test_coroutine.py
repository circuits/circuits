#!/usr/bin/env python

import pytest

from circuits import Component, Event

pytestmark = pytest.mark.skip("XXX: This test fails intermittently")


class test(Event):

    """test Event"""


class coroutine1(Event):

    """coroutine Event"""

    complete = True


class coroutine2(Event):

    """coroutine Event"""

    complete = True


class App(Component):

    returned = False

    def test(self, event):
        event.stop()
        return "Hello World!"

    def coroutine1(self):
        print("coroutine1")
        yield self.call(test())
        print("returned")
        self.returned = True

    def coroutine2(self):
        print("coroutine2")
        self.fire(test())
        yield self.wait("test")
        print("returned")
        self.returned = True


@pytest.fixture
def app(simple_manager):
    return App().register(simple_manager)


def test_coroutine(simple_manager, app):
    simple_manager.fire(coroutine1())
    assert simple_manager.run_until("coroutine1_complete")
    assert app.returned, "coroutine1"

    app.returned = False
    simple_manager.fire(coroutine2())
    assert simple_manager.run_until("coroutine2_complete")
    assert app.returned, "coroutine2"
