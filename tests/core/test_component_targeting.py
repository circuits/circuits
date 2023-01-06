#!/usr/bin/env python
import pytest

from circuits import Component, Event


class hello(Event):

    """hello Event"""

    success = True


class App(Component):

    channel = "app"

    def hello(self):
        return "Hello World!"


@pytest.fixture
def app(simple_manager):
    return App().register(simple_manager)


def test(simple_manager, app):
    x = simple_manager.fire(hello(), app)
    assert simple_manager.run_until("hello_success")

    value = x.value
    assert value == "Hello World!"
