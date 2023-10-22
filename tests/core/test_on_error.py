#!/usr/bin/env python

"""Tests on_error behaviour"""


import pytest

from circuits import Component, Event, handler


class test(Event):
    """test Event"""

    on_error = "abort"


class App(Component):

    @handler(priority=1)
    def on_event(self, event, *args, **kwargs):
        if kwargs.get("error", False):
            raise Exception("XXX")

    def test(self, error=None):
        return "Hello World!"


@pytest.fixture()
def app(request):
    return App()


def test_no_error(app):
    x = app.fire(test())
    app.tick()

    assert x.value == "Hello World!"


def test_on_error(app):
    x = app.fire(test(error=True))
    app.tick()

    assert isinstance(x[1], Exception)
    assert x[1].args[0] == "XXX"
