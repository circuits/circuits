#!/usr/bin/env python

import pytest

from circuits import Component
from circuits.io import File, Write, Close


class App(Component):

    def __init__(self, *args, **kwargs):
        super(App, self).__init__()

        self.file = File(*args, **kwargs)
        self.file.register(self)

        self.data = None
        self.eof = False

    def read(self, data):
        self.data = data

    def eof(self):
        self.eof = True


def test_write(tmpdir):
    sockpath = tmpdir.ensure("helloworld.txt")
    filename = str(sockpath)

    app = App(filename, "w")
    waiter = pytest.WaitEvent(app, "opened")
    app.start()
    assert waiter.wait()

    app.fire(Write(b"Hello World!"), app.file)

    waiter = pytest.WaitEvent(app, "closed")
    app.fire(Close(), app.file)
    assert waiter.wait()

    app.stop()

    f = open(filename, "r")
    s = f.read()
    assert s == "Hello World!"


def test_read(tmpdir):
    sockpath = tmpdir.ensure("helloworld.txt")
    filename = str(sockpath)

    f = open(filename, "w")
    f.write("Hello World!")
    f.close()

    app = App(filename, "r")
    waiter = pytest.WaitEvent(app, "opened")
    app.start()
    assert waiter.wait()

    while not app.eof:
        pass

    app.stop()

    assert app.data == b"Hello World!"


def test_fd(tmpdir):
    sockpath = tmpdir.ensure("helloworld.txt")
    filename = str(sockpath)

    f = open(filename, "w")
    f.write("Hello World!")
    f.close()

    app = App(open(filename, "r"))
    waiter = pytest.WaitEvent(app, "opened")
    app.start()
    assert waiter.wait()
