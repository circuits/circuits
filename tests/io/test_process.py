#!/usr/bin/env python

import pytest
if pytest.PLATFORM == "win32":
    pytest.skip("Unsupported Platform")

from circuits.io import Process, write


def test(manager, watcher):
    p = Process(["echo", "Hello World!"]).register(manager)
    assert watcher.wait("registered")

    p.start()
    assert watcher.wait("started", p.channel)

    assert watcher.wait("stopped", p.channel)

    s = p.stdout.getvalue()
    assert s == b"Hello World!\n"


def test2(manager, watcher, tmpdir):
    foo = tmpdir.ensure("foo.txt")

    p = Process(["cat - > {0:s}".format(str(foo))], shell=True).register(manager)
    assert watcher.wait("registered")

    p.start()
    assert watcher.wait("started", p.channel)

    p.fire(write("Hello World!"), p._stdin)
    assert watcher.wait("write", p._stdin)

    p.stop()

    assert watcher.wait("eof", p._stdout.channel)

    with foo.open("r") as f:
        assert f.read() == "Hello World!"
