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
def app(request, manager, watcher):
    app = App().register(manager)
    assert watcher.wait("registered")

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    return app


def test(manager, watcher, app):
    x = manager.fire(hello(), app)
    assert watcher.wait("hello_success")

    value = x.value
    assert value == "Hello World!"
