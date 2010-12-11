# Module:   test_timers
# Date:     10th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Timers Tests"""

from datetime import datetime, timedelta

import py

from circuits import Event, Component, Timer

def pytest_funcarg__app(request):
    return request.cached_setup(
            setup=lambda: setupapp(request),
            teardown=lambda app: teardownapp(app),
            scope="module")

def setupapp(request):
    app = App()
    app.start()
    return app

def teardownapp(app):
    app.stop()

class Test(Event):
    """Test Event"""

class App(Component):

    flag = False

    def reset(self):
        self.flag = False

    def timer(self):
        self.flag = True

def test_timer(app):
    timer = Timer(0.1, Test(), "timer")
    timer.register(app)
    assert py.test.wait_for(app, "flag")
    app.reset()

def test_persistentTimer(app):
    timer = Timer(0.1, Test(), "timer", persist=True)
    timer.register(app)

    for i in xrange(2):
        assert py.test.wait_for(app, "flag")
        app.reset()

    timer.unregister()

def test_datetime(app):
    now = datetime.now()
    d = now + timedelta(seconds=0.1)
    timer = Timer(d, Test(), "timer")
    timer.register(app)
    assert py.test.wait_for(app, "flag")
    app.reset()
