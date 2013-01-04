#!/usr/bin/env python


import sys

from circuits.io import Process, Start

from tests.io import hello


def test(manager, watcher):
    p = Process([sys.executable, hello.__file__]).register(manager)
    assert watcher.wait("registered")

    p.fire(Start())
    assert watcher.wait("started", p.channel)

    assert watcher.wait("stopped", p.channel)

    s = p.stdout.getvalue()
    assert s == "Hello World!\n"
