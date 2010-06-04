# Module:   test_timers
# Date:     10th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Timers Tests"""

from time import sleep
from datetime import datetime, timedelta

from circuits import Event, Component, Timer

class Test(Event):
    """Test Event"""

class App(Component):

    flag = False

    def timer(self):
        self.flag = True

app = App()
app.start()

def test_timer():
    timer = Timer(0.1, Test(), "timer")
    timer.register(app)
    sleep(0.2)
    assert app.flag

def test_persistentTimer():
    timer = Timer(0.1, Test(), "timer", persist=True)
    timer.register(app)

    for i in xrange(2):
        sleep(0.2)
        assert app.flag
        app.flag = False

    timer.unregister()

def test_datetime():
    now = datetime.now()
    d = now + timedelta(seconds=1)
    timer = Timer(d, Test(), "timer")
    timer.register(app)
    sleep(1)
    assert app.flag
