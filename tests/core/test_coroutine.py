#!/usr/bin/env python
from __future__ import print_function

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
def app(request, manager, watcher):
    app = App().register(manager)
    assert watcher.wait("registered")

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    return app


def test_coroutine(manager, watcher, app):
    manager.fire(coroutine1())
    assert watcher.wait("coroutine1_complete")
    assert app.returned, "coroutine1"

    app.returned = False
    manager.fire(coroutine2())
    assert watcher.wait("coroutine2_complete")
    assert app.returned, "coroutine2"
