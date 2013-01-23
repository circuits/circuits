#!/usr/bin/env python

from circuits.io import Process, Start


def test(manager, watcher):
    p = Process(["echo", "Hello World!"]).register(manager)
    assert watcher.wait("registered")

    p.fire(Start())
    assert watcher.wait("started", p.channel)

    assert watcher.wait("stopped", p.channel)

    s = p.stdout.getvalue()
    assert s == "Hello World!\n"
