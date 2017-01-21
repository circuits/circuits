#!/usr/bin/env python
import pytest

from circuits import Component, Event


class App(Component):

    def init(self):
        self._ready = False
        self._done = False
        self._counter = 0

    def registered(self, component, manager):
        if component is self:
            self.fire(Event.create("ready"))

    def generate_events(self, event):
        if not self._ready or self._done:
            return

        if self._counter < 10:
            self.fire(Event.create("hello"))
        else:
            self.fire(Event.create("done"))
        event.reduce_time_left(0)

    def done(self):
        self._done = True

    def hello(self):
        self._counter += 1

    def ready(self):
        self._ready = True


@pytest.fixture
def app(request, manager, watcher):
    app = App().register(manager)

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    assert watcher.wait("ready")

    return app


def test(manager, watcher, app):
    watcher.wait("done")
    assert app._counter == 10
