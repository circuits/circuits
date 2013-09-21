#!/usr/bin/env python

import pytest
if pytest.PLATFORM == "win32":
    pytest.skip("Unsupported Platform")

from circuits.io import Process


def test(manager, watcher):
    p = Process(["echo", "Hello World!"]).register(manager)
    assert watcher.wait("registered")

    p.start()
    assert watcher.wait("started", p.channel)

    assert watcher.wait("stopped", p.channel)

    s = p.stdout.getvalue()
    assert s == b"Hello World!\n"
