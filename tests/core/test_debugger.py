"""Debugger Tests"""

import sys

import pytest

from circuits import Debugger
from circuits.core import Component, Event

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # NOQA


class test(Event):
    """test Event"""


class App(Component):

    def test(self, raiseException=False):
        if raiseException:
            raise Exception()


class Logger(object):

    error_msg = None
    debug_msg = None

    def error(self, msg):
        self.error_msg = msg

    def debug(self, msg):
        self.debug_msg = msg


def test_main():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while len(app):
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger._events

    e = Event()
    app.fire(e)
    app.flush()
    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    debugger._events = False
    assert not debugger._events

    e = Event()
    app.fire(e)

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()


def test_file(tmpdir):
    logfile = str(tmpdir.ensure("debug.log"))
    stderr = open(logfile, "w+")

    app = App()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while len(app):
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger._events

    e = Event()
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    debugger._events = False
    assert not debugger._events

    e = Event()
    app.fire(e)

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()


def test_filename(tmpdir):
    if "__pypy__" in sys.modules:
        pytest.skip("Broken on pypy")

    logfile = str(tmpdir.ensure("debug.log"))
    stderr = open(logfile, "r+")

    app = App()
    debugger = Debugger(file=logfile)
    debugger.register(app)
    while len(app):
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger._events

    e = Event()
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    debugger._events = False
    assert not debugger._events

    e = Event()
    app.fire(e)

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()


def test_exceptions():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while len(app):
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger._events
    assert debugger._errors

    e = test(raiseException=True)
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    app.flush()
    stderr.seek(0)
    s = stderr.read().strip()
    assert s.startswith("<exception[*]")
    stderr.seek(0)
    stderr.truncate()

    debugger._events = False
    debugger._errors = False

    assert not debugger._events
    assert not debugger._errors

    e = test(raiseException=True)
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()

    app.flush()
    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""


def test_IgnoreEvents():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while len(app):
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger._events

    debugger.IgnoreEvents.extend(["test"])

    e = Event()
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    e = test()
    app.fire(e)
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
    while len(app):
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger._events
    debugger.IgnoreChannels.extend([("*", "test")])

    e = Event()
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    e = test()
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()


def test_Logger_debug():
    app = App()
    logger = Logger()
    debugger = Debugger(logger=logger)
    debugger.register(app)
    while len(app):
        app.flush()

    e = Event()
    app.fire(e)
    app.flush()

    assert logger.debug_msg == repr(e)


def test_Logger_error():
    app = App()
    logger = Logger()
    debugger = Debugger(logger=logger)
    debugger.register(app)
    while len(app):
        app.flush()

    e = test(raiseException=True)
    app.fire(e)
    while len(app):
        app.flush()

    assert logger.error_msg.startswith("ERROR <handler[*][test] (App.test)> (")
