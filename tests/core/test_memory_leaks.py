#!/usr/bin/env python
import pytest

from circuits import Component, Event, handler


class call(Event):

    """call Event"""
    success = True


class hello(Event):

    """hello Event"""
    success = True


class App(Component):
    @handler("call")
    def _on_call(self):
        x = yield self.call(hello())
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


def test_done_handlers_dont_leak(manager, watcher, app):
    manager.fire(call())
    manager.fire(call())
    assert watcher.wait("call_success")
    assert "hello_done" not in app._handlers
