# Module:   test_timers
# Date:     10th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au
import time

"""Timers Tests"""

import pytest

from datetime import datetime, timedelta

from circuits import Event, Component, Timer


def pytest_funcarg__app(request):
    return request.cached_setup(
        setup=lambda: setupapp(request),
        teardown=lambda app: teardownapp(app),
        scope="module"
    )


def setupapp(request):
    app = App()
    app.start()
    return app


def teardownapp(app):
    app.stop()


class test(Event):
    """test Event"""


class App(Component):

    def __init__(self):
        super(App, self).__init__()
        self.flag = False
        self.count = 0
        self.timestamps = []

    def reset(self):
        self.timestamps = []
        self.flag = False
        self.count = 0

    def test(self):
        self.timestamps.append(time.time())
        self.count += 1
        self.flag = True


def test_timer(app):
    timer = Timer(0.1, test(), "timer")
    timer.register(app)
    assert pytest.wait_for(app, "flag")
    app.reset()


def test_persistentTimer(app):
    app.timestamps.append(time.time())
    timer = Timer(0.2, test(), "timer", persist=True)
    timer.register(app)

    wait_res = pytest.wait_for(app, "count", 2)
    assert app.count >= 2
    assert wait_res
    delta = app.timestamps[1] - app.timestamps[0]
    # Should be 0.1, but varies depending on timer precision and load
    assert delta >= 0.08 and delta < 0.5
    delta = app.timestamps[2] - app.timestamps[1]
    assert delta >= 0.08 and delta < 0.5
    app.reset()

    timer.unregister()


def test_datetime(app):
    now = datetime.now()
    d = now + timedelta(seconds=0.1)
    timer = Timer(d, test(), "timer")
    timer.register(app)
    assert pytest.wait_for(app, "flag")
    app.reset()
