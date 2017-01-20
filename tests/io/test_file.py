#!/usr/bin/env python
from io import BytesIO

import pytest

from circuits import Component
from circuits.io import File
from circuits.io.events import close, write

pytestmark = pytest.mark.skipif(pytest.PLATFORM == 'win32', reason='Unsupported Platform')


class FileApp(Component):

    def init(self, *args, **kwargs):
        self.file = File(*args, **kwargs).register(self)

        self.eof = False
        self.closed = False
        self.buffer = BytesIO()

    def read(self, data):
        self.buffer.write(data)

    def eof(self):
        self.eof = True

    def closed(self):
        self.closed = True


def test_open_fileobj(manager, watcher, tmpdir):
    filename = str(tmpdir.ensure("helloworld.txt"))
    with open(filename, "w") as f:
        f.write("Hello World!")

    fileobj = open(filename, "r")

    app = FileApp(fileobj).register(manager)
    assert watcher.wait("opened", app.file.channel)

    assert watcher.wait("eof", app.file.channel)
    assert app.eof

    app.fire(close(), app.file.channel)
    assert watcher.wait("closed", app.file.channel)
    assert app.closed

    app.unregister()
    assert watcher.wait("unregistered")

    s = app.buffer.getvalue()
    assert s == b"Hello World!"


def test_read_write(manager, watcher, tmpdir):
    filename = str(tmpdir.ensure("helloworld.txt"))

    app = FileApp(filename, "w").register(manager)
    assert watcher.wait("opened", app.file.channel)

    app.fire(write(b"Hello World!"), app.file.channel)
    assert watcher.wait("write", app.file.channel)

    app.fire(close(), app.file.channel)
    assert watcher.wait("closed", app.file.channel)
    assert app.closed

    app.unregister()
    assert watcher.wait("unregistered")

    app = FileApp(filename, "r").register(manager)
    assert watcher.wait("opened", app.file.channel)

    assert watcher.wait("eof", app.file.channel)
    assert app.eof

    app.fire(close(), app.file.channel)
    assert watcher.wait("closed", app.file.channel)
    assert app.closed

    app.unregister()
    assert watcher.wait("unregistered")

    s = app.buffer.getvalue()
    assert s == b"Hello World!"
