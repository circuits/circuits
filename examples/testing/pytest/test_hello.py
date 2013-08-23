#!/usr/bin/env python

import pytest

from hello import Hello, App


@pytest.fixture
def app(request, manager, watcher):
    app = App().register(manager)
    watcher.wait("registered")

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    return app


def test(app, watcher):
    x = app.fire(Hello())
    assert watcher.wait("hello")

    assert x.value == "Hello World!"
