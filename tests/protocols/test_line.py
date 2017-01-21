#!/usr/bin/env python
from collections import defaultdict

from circuits import Component, Event
from circuits.protocols import Line


class read(Event):

    """read Event"""


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
    Line().register(app)

    while len(app):
        app.flush()

    app.fire(read(b"1\n2\r\n3\n4"))

    while len(app):
        app.flush()

    assert app.lines[0] == b"1"
    assert app.lines[1] == b"2"
    assert app.lines[2] == b"3"


def test_server():
    app = AppServer()
    buffers = defaultdict(bytes)
    Line(
        getBuffer=buffers.__getitem__,
        updateBuffer=buffers.__setitem__
    ).register(app)

    while len(app):
        app.flush()

    app.fire(read(1, b"1\n2\r\n3\n4"))
    app.fire(read(2, b"1\n2\r\n3\n4"))

    while len(app):
        app.flush()

    assert app.lines[0] == (1, b"1")
    assert app.lines[1] == (1, b"2")
    assert app.lines[2] == (1, b"3")

    assert app.lines[3] == (2, b"1")
    assert app.lines[4] == (2, b"2")
    assert app.lines[5] == (2, b"3")
