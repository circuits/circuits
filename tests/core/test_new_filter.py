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
def app(request, manager, watcher):
    app = (App() + App()).register(manager)
    watcher.wait("registered")

    def finalizer():
        app.unregister()
        watcher.wait("unregistered")

    request.addfinalizer(finalizer)

    return app


def test_normal(app, watcher):
    x = app.fire(hello())
    watcher.wait("hello_success")
    assert x.value == ["Hello World!", "Hello World!"]


def test_filter(app, watcher):
    x = app.fire(hello(stop=True))
    watcher.wait("hello_success")
    assert x.value == "Hello World!"
