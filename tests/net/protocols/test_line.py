#!/usr/bin/env python

from circuits import Event, Component
from circuits.net.protocols import LP

class Read(Event):
    """Read Event"""

class App(Component):

    lines = []

    def line(self, line):
        self.lines.append(line)

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
