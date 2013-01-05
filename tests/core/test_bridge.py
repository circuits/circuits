#!/usr/bin/python -i

from os import getpid

import pytest
pytest.importorskip("multiprocessing")

from circuits import Event, Component


class Hello(Event):
    """Hello Event"""


class App(Component):

    def hello(self):
        return "Hello from {0:d}".format(getpid())


def test():
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
