#!/usr/bin/python -i

from os import getpid

import pytest
pytest.importorskip("multiprocessing")

from circuits import Component, Event


class Hello(Event):
    """Hello Event"""


class App(Component):

    def hello(self):
        return "Hello from {0:d}".format(getpid())


def test_parent_child():
    app = App()
    waiter = pytest.WaitEvent(app, "ready")
    app.start(process=True, link=True)
    assert waiter.wait()

    x = app.fire(Hello())

    def test(obj, attr):
        return isinstance(obj._value, list)

    assert pytest.wait_for(x, None, test)

    expected_set = set(
        [
            "Hello from {0:d}".format(getpid()),
            "Hello from {0:d}".format(app._process.pid)
        ]
    )

    actual_set = set(x.value)

    assert actual_set == expected_set

    app.stop()


def test_child(manager, watcher):
    app = App()
    app.start(process=True, link=manager)
    assert watcher.wait("ready")

    x = manager.fire(Hello())

    assert pytest.wait_for(x, "result")

    assert x.value == "Hello from {0:d}".format(app._process.pid)

    app.stop()
