#!/usr/bin/env python
from random import random, seed
from time import sleep, time

import pytest

from circuits.core import Component, Event, Worker, handler, task


class hello(Event):

    """hello Event"""

    success = True


def process(x=None):
    sleep(random())
    return x


class App(Component):

    @handler('hello')
    def _on_hello(self):
        e1 = task(process, 1)
        self.fire(task(process, 2))
        self.fire(task(process, 3))
        yield (yield self.call(e1))


@pytest.fixture
def app(request, manager, watcher):
    seed(time())

    app = App().register(manager)
    assert watcher.wait("registered")

    worker = Worker().register(manager)
    assert watcher.wait("registered")

    def finalizer():
        app.unregister()
        worker.unregister()

    request.addfinalizer(finalizer)

    return app


def test_call_order(manager, watcher, app):
    x = manager.fire(hello())
    assert watcher.wait('hello_success')

    value = x.value

    assert value == 1
