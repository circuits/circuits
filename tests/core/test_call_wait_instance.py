#!/usr/bin/env python
import pytest

from circuits import Component, Event, handler


class wait(Event):
    """wait Event"""

    success = True


class hello(Event):
    """hello Event"""

    success = True


class App(Component):

    @handler("wait")
    def _on_wait(self):
        e = hello()
        x = self.fire(e)
        yield self.wait(e)
        yield x.value

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


def test_wait_instance(manager, watcher, app):
    x = manager.fire(wait())
    assert watcher.wait("wait_success")

    value = x.value
    assert value == "Hello World!"
