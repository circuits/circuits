#!/usr/bin/python -i
from os import getpid

import pytest

from circuits import Component, Event, ipc


pytestmark = pytest.mark.skipif(pytest.PLATFORM == 'win32', reason='Unsupported Platform')

pytest.importorskip('multiprocessing')


class hello(Event):
    """hello Event"""


class App(Component):
    def hello(self):
        return f'Hello from {getpid():d}'


def test(manager, watcher):
    app = App()
    _process, bridge = app.start(process=True, link=manager)
    assert watcher.wait('ready')

    x = manager.fire(ipc(hello()))

    assert pytest.wait_for(x, 'result')

    assert x.value == f'Hello from {app.pid:d}'

    app.stop()
    app.join()

    bridge.unregister()
    watcher.wait('unregistered')
