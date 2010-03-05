#!/usr/bin/env python

from collections import defaultdict

from circuits import Event, Component
from circuits.net.protocols import LP

class Read(Event):
    """Read Event"""

class App(Component):

    lines = []

    def line(self, line):
        self.lines.append(line)

class AppServer(Component):

    channel = "server"

    lines = []

    def line(self, sock, line):
        self.lines.append((sock, line))

def test():
    app = App()
    LP().register(app)

    while app:
        app.flush()

    app.push(Read("1\n2\r\n3\n4"))

    while app:
        app.flush()

    assert app.lines[0] == "1"
    assert app.lines[1] == "2"
    assert app.lines[2] == "3"

def test_server():
    app = AppServer()
    buffers = defaultdict(str)
    LP(getBuffer=buffers.__getitem__,
            updateBuffer=buffers.__setitem__).register(app)

    while app:
        app.flush()

    app.push(Read(1, "1\n2\r\n3\n4"))
    app.push(Read(2, "1\n2\r\n3\n4"))

    while app:
        app.flush()

    assert app.lines[0] == (1, "1")
    assert app.lines[1] == (1, "2")
    assert app.lines[2] == (1, "3")

    assert app.lines[3] == (2, "1")
    assert app.lines[4] == (2, "2")
    assert app.lines[5] == (2, "3")
