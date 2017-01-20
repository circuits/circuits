#!/usr/bin/env python
import pytest

from circuits.io import Process, write

if pytest.PLATFORM == "win32":
    pytest.skip("Unsupported Platform")


def test(manager, watcher):
    p = Process(["echo", "Hello World!"]).register(manager)
    assert watcher.wait("registered")

    p.start()
    assert watcher.wait("started", p.channel)

    assert watcher.wait("terminated", p.channel)

    s = p.stdout.getvalue()
    assert s == b"Hello World!\n"


def test2(manager, watcher, tmpdir):
    foo = tmpdir.ensure("foo.txt")

    p = Process(
        ["cat - > {0:s}".format(str(foo))], shell=True).register(manager)
    assert watcher.wait("registered")

    p.start()
    assert watcher.wait("started", p.channel)

    p.fire(write("Hello World!"), p._stdin)
    assert watcher.wait("write", p._stdin)

    p.stop()

    assert watcher.wait("eof", p._stdout.channel)

    with foo.open("r") as f:
        assert f.read() == "Hello World!"


def test_two_procs(manager, watcher):
    p1 = Process(["echo", "1"]).register(manager)
    p2 = Process("echo 2 ; sleep 1", shell=True).register(manager)

    p1.start()
    p2.start()

    assert watcher.wait("terminated", p1.channel)
    assert p1._terminated
    assert not p2._terminated
    assert not p2._stdout_closed
    assert not p2._stderr_closed

    watcher.clear()     # Get rid of first terminated()

    s1 = p1.stdout.getvalue()
    assert s1 == b"1\n"

    assert watcher.wait("terminated", p2.channel)
    assert p2._terminated
    assert p2._stdout_closed
    assert p2._stderr_closed

    s2 = p2.stdout.getvalue()
    assert s2 == b"2\n"
