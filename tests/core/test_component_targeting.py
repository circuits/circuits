#!/usr/bin/env python


import pytest
pytest.skip("XXX: Missing Feature")

from circuits import Component, Event


class App(Component):

    channel = "app"

    def hello(self):
        return "Hello World!"

    def registered(self, component, manager):
        if component is self:
            self.fire(Event.create("Ready"))


@pytest.fixture(scope="module")
def app(request, manager, watcher):
    app = App().register(manager)

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    assert watcher.wait("ready")

    return app


def test(manager, watcher, app):
    x = manager.fire(Event.create("Hello"), app)
    assert watcher.wait("hello")
    assert x == "Hello World!"
