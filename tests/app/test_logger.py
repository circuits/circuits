#!/usr/bin/env python

from time import strftime

from circuits import Event, Component
from circuits.app.log import Log, Logger

LEVELS = Logger.LEVELS.keys()

class Test(Event):
    """Test Event"""

class App(Component):

    def test(self, level="debug"):
        self.push(Log(level, "Hello World!"))

def test(tmpdir):
    filepath = tmpdir.ensure("test.log")
    filename = str(filepath)

    app = App()
    logger = Logger(filename, "test", "file", "DEBUG")
    logger.register(app)

    while app:
        app.flush()

    f = open(filename, "r+")

    def test(f, level="debug"):
        app.push(Test(level))
        while app:
            app.flush()
        now = strftime("%H:%M:%S")
        f.seek(0)
        s = f.read().strip()
        if level == "exception":
            level = "error"
        elif level == "warn":
            level = "warning"
        assert s == "%s test[log] %s: Hello World!" % (now, level.upper()) or \
            s[(len(now) + 1):] == "test[log] %s: Hello World!" % (level.upper())
    for level in LEVELS:
        f.seek(0)
        f.truncate()
        test(f, level)

def test_direct(tmpdir):
    filepath = tmpdir.ensure("test.log")
    filename = str(filepath)

    logger = Logger(filename, "test", "file", "DEBUG")

    f = open(filename, "r+")

    def test(f, level="debug"):
        getattr(logger, level)("Hello World!")
        f.seek(0)
        now = strftime("%H:%M:%S")
        s = f.read().strip()
        if level == "warn":
            level = "warning"
        if level == "exception":
            assert s == "%s test[log] ERROR: Hello World!\nNone" % now or \
                s[(len(now) + 1):] == "test[log] ERROR: Hello World!\nNone"
        else:
            assert s == "%s test[log] %s: Hello World!" % (now, level.upper()) or \
                s[(len(now) + 1):] == "test[log] %s: Hello World!" % level.upper()

    for level in LEVELS:
        f.seek(0)
        f.truncate()
        test(f, level)
