#!/usr/bin/env python
import pytest

from circuits import Component, Event


class hello(Event):

    """hello Event"""

    success = True


class App(Component):

    def hello(self, event, *args, **kwargs):
        if kwargs.get("stop", False):
            event.stop()
        return "Hello World!"


@pytest.fixture
def app(simple_manager):
    return (App() + App()).register(simple_manager)


def test_normal(app, simple_manager):
    x = app.fire(hello())
    assert simple_manager.run_until("hello_success")
    assert x.value == ["Hello World!", "Hello World!"]


def test_filter(app, simple_manager):
    x = app.fire(hello(stop=True))
    assert simple_manager.run_until("hello_success")
    assert x.value == "Hello World!"
