#!/usr/bin/env python

import pytest
if pytest.PLATFORM == "win32":
    pytest.skip("Unsupported Platform")

from io import BytesIO
from circuits import Component
from circuits.io import File, Write, Close


class FileApp(Component):

    def init(self, *args, **kwargs):
        self.file = File(*args, **kwargs).register(self)

        self.eof = False
        self.buffer = BytesIO()

    def read(self, data):
        self.buffer.write(data)

    def eof(self):
        self.eof = True


def test_open_fileobj(manager, watcher, tmpdir):
    filename = str(tmpdir.ensure("helloworld.txt"))
    with open(filename, "w") as f:
        f.write("Hello World!")

    fileobj = open(filename, "r")
    print(type(fileobj))

    app = FileApp(fileobj).register(manager)
    assert watcher.wait("opened", app.file.channel)

    assert watcher.wait("eof", app.file.channel)

    app.fire(Close(), app.file.channel)
    assert watcher.wait("closed", app.file.channel)

    app.unregister()
    assert watcher.wait("unregistered")

    s = app.buffer.getvalue()
    assert s == b"Hello World!"


def test_read_write(manager, watcher, tmpdir):
    filename = str(tmpdir.ensure("helloworld.txt"))

    app = FileApp(filename, "w").register(manager)
    assert watcher.wait("opened", app.file.channel)

    app.fire(Write(b"Hello World!"), app.file.channel)
    assert watcher.wait("write", app.file.channel)

    app.fire(Close(), app.file.channel)
    assert watcher.wait("closed", app.file.channel)

    app.unregister()
    assert watcher.wait("unregistered")

    app = FileApp(filename, "r").register(manager)
    assert watcher.wait("opened", app.file.channel)

    assert watcher.wait("eof", app.file.channel)

    app.fire(Close(), app.file.channel)
    assert watcher.wait("closed", app.file.channel)

    app.unregister()
    assert watcher.wait("unregistered")

    s = app.buffer.getvalue()
    assert s == b"Hello World!"
