#!/usr/bin/python -i


import pytest


from os import getpid
from time import sleep


from circuits import ipc, Component, Event


if pytest.PLATFORM == "win32":
    pytest.skip("Unsupported Platform")


pytest.importorskip("multiprocessing")


class hello(Event):
    """hello Event"""


class App(Component):

    def hello(self):
        return "Hello from {0:d}".format(getpid())


def test(manager, watcher):
    app = App()
    process, bridge = app.start(process=True, link=manager)
    assert watcher.wait("ready")

    x = manager.fire(ipc(hello()))

    assert pytest.wait_for(x, "result")

    assert x.value == "Hello from {0:d}".format(app.pid)

    app.stop()
    app.join()

    bridge.unregister()
    watcher.wait("unregistered")
