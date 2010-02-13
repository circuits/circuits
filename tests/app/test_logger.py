#!/usr/bin/env python

from time import strftime
from tempfile import mkstemp

from circuits import Event, Component
from circuits.app.log import Log, Logger, DEBUG

class Test(Event):
    """Test Event"""

class App(Component):

    def test(self):
        self.push(Log(DEBUG, "Hello World!"))

def test():
    fd, filename = mkstemp()
    app = App() + Logger(filename, "test", "file", "DEBUG")
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
