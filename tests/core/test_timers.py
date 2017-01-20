"""Timers Tests"""


from datetime import datetime, timedelta
from itertools import starmap
from operator import sub
from time import time

import pytest

from circuits import Component, Event, Timer, sleep
from circuits.six.moves import map, zip


@pytest.fixture
def app(request, manager, watcher):
    app = App().register(manager)
    assert watcher.wait("registered")

    def finalizer():
        app.unregister()
        assert watcher.wait("unregistered")

    request.addfinalizer(finalizer)

    return app


class single(Event):

    """single Event"""

    complete = True


class persistent(Event):

    """persistent Event"""

    complete = True


class App(Component):

    def init(self):
        self.flag = False
        self.count = 0
        self.timestamps = []

    def single(self):
        self.timestamps.append(time())
        self.count += 1
        self.flag = True

    def persistent(self, interval):
        timer = Timer(interval, single(), persist=True)
        timer.register(self)

        yield sleep(interval * 10)

        timer.unregister()


def test_single(app, watcher):
    Timer(0.1, single()).register(app)
    assert watcher.wait("single_complete")
    assert app.flag


def test_persistent(app, watcher):
    exponent = -1
    interval = 10.0 ** exponent
    app.fire(persistent(interval))
    assert watcher.wait("persistent_complete")

    xs = list(map(abs, starmap(sub, zip(app.timestamps, app.timestamps[1:]))))
    avg = sum(xs) / len(xs)

    assert round(avg, abs(exponent)) == interval


def test_datetime(app, watcher):
    now = datetime.now()
    d = now + timedelta(seconds=0.1)
    Timer(d, single()).register(app)
    assert watcher.wait("single_complete")
    assert app.flag
