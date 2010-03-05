#!/usr/bin/env python

from time import strftime

from circuits import Event, Component
from circuits.app.log import Log, Logger

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

    app.push(Test())

    while app:
        app.flush()

    now = strftime("%H:%M:%S")
    f = open(filename, "r")
    s = f.read().strip()
    f.close()

    assert s == "%s test[log] DEBUG: Hello World!" % now
