"""Manager Repr Tests

Test Manager's representation string.
"""
import os
from threading import current_thread
from time import sleep

import pytest

from circuits import Component, Manager


class App(Component):

    def test(self, event, *args, **kwargs):
        pass


def test_main():
    id = "%s:%s" % (os.getpid(), current_thread().getName())

    m = Manager()
    assert repr(m) == "<Manager/ %s (queued=0) [S]>" % id

    app = App()
    app.register(m)
    s = repr(m)
    assert s == "<Manager/ %s (queued=1) [S]>" % id

    m.start()

    pytest.wait_for(m, "_running", True)
    sleep(0.1)

    s = repr(m)
    assert s == "<Manager/ %s (queued=0) [R]>" % id

    m.stop()

    pytest.wait_for(m, "_Manager__thread", None)

    s = repr(m)
    assert s == "<Manager/ %s (queued=0) [S]>" % id
