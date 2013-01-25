#!/usr/bin/env python

from time import strftime

from circuits import Event, Component
from circuits.app.log import Log, Logger

LEVELS = list(Logger.LEVELS.keys())

class Test(Event):
    """Test Event"""

class App(Component):

    def test(self, level="debug"):
        self.fire(Log(level, "Hello World!"))

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
        app.fire(Test(level))
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
            assert s[:len(now)+31] == "%s test[log] ERROR: Hello World!\n" % now or \
                s[(len(now) + 1):(len(now) + 1)+31] == "test[log] ERROR: Hello World!\n"
        else:
            assert s == "%s test[log] %s: Hello World!" % (now, level.upper()) or \
                s[(len(now) + 1):] == "test[log] %s: Hello World!" % level.upper()

    for level in LEVELS:
        f.seek(0)
        f.truncate()
        if level == 'exception':
            try:
                raise Exception()
            except:
                test(f, level)
        else:
            test(f, level)
