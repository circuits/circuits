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


def test(manager, watcher):
    app = App()
    app.start(process=True, link=manager)
    assert watcher.wait("ready")

    x = manager.fire(Hello())

    assert pytest.wait_for(x, "result")

    assert x.value == "Hello from {0:d}".format(app.pid)

    app.stop()
