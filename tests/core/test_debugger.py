# Module:   debugger
# Date:     5th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Debugger Tests"""

from time import sleep
from StringIO import StringIO

from circuits import Debugger
from circuits.core import handler, Event, Component, Manager


class Test(Event):
    """Test Event"""

class App(Component):

    def test(self):
        pass

class Logger(object):

    msg = None

    def debug(self, msg):
        self.msg = msg

def test():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events

    e = Event()
    app.push(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    debugger.events = False
    assert not debugger.events

    e = Event()
    app.push(e)

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()

def test_IgnoreEvents():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events

    debugger.IgnoreEvents.extend([Test])

    e = Event()
    app.push(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    e = Test()
    app.push(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()

def test_IgnoreChannels():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events
    debugger.IgnoreChannels.extend([("*", "test")])

    e = Event()
    app.push(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    e = Test()
    app.push(e)

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()

def test_Logger():
    app = App()
    logger = Logger()
    debugger = Debugger(logger=logger)
    debugger.register(app)
    while app:
        app.flush()

    e = Event()
    app.push(e)
    app.flush()

    assert logger.msg == repr(e)
