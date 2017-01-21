#!/usr/bin/env python
import pytest
from hello import App, hello


@pytest.fixture
def app(request, manager, watcher):
    app = App().register(manager)
    watcher.wait("registered")

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    return app


def test(app, watcher):
    x = app.fire(hello())
    assert watcher.wait("hello")

    assert x.value == "Hello World!"
