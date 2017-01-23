#!/usr/bin/env python

from __future__ import print_function

import pytest

from circuits import Component, Event, handler


class test(Event):
    """test Event"""

    success = True


class foo(Event):
    """foo Event"""


class App(Component):

    @handler("test", priority=1)
    def on_test(self, event):
        event.stop()
        yield

    @handler("test")
    def on_test_ignored(self):
        return "Hello World!"


@pytest.fixture
def app(request):
    return App()


def test_call_stop(app):
    x = app.fire(test())
    app.tick()

    assert x.value is None
