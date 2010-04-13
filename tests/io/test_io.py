#!/usr/bin/env python

from time import sleep

from circuits import Component
from circuits.io import File, Write

class App(Component):

    def __init__(self, *args):
        super(App, self).__init__()

        self._file = File(*args)
        self._file.register(self)

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
    app.start()
    app.push(Write("Hello World!"))
    sleep(1)
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
    app.start()

    while not app.eof:
        pass

    app.stop()

    assert app.data == "Hello World!"

def test_fd(tmpdir):
    sockpath = tmpdir.ensure("helloworld.txt")
    filename = str(sockpath)

    f = open(filename, "w")
    f.write("Hello World!")
    f.close()

    app = App(open(filename, "r"))
    app.start()

    while not app.eof:
        pass

    app.stop()

    assert app.data == "Hello World!"
