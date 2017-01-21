"""Component Repr Tests

Test Component's representation string.
"""
import os

from circuits import Component, Event

try:
    from threading import current_thread
except ImportError:
    from threading import currentThread as current_thread  # NOQA


class App(Component):

    def test(self, event, *args, **kwargs):
        pass


class test(Event):
    pass


def test_main():
    id = "%s:%s" % (os.getpid(), current_thread().getName())
    app = App()

    assert repr(app) == "<App/* %s (queued=0) [S]>" % id

    app.fire(test())
    assert repr(app) == "<App/* %s (queued=1) [S]>" % id

    app.flush()
    assert repr(app) == "<App/* %s (queued=0) [S]>" % id


def test_non_str_channel():
    id = "%s:%s" % (os.getpid(), current_thread().getName())
    app = App(channel=(1, 1))

    assert repr(app) == "<App/(1, 1) %s (queued=0) [S]>" % id

    app.fire(test())
    assert repr(app) == "<App/(1, 1) %s (queued=1) [S]>" % id

    app.flush()
    assert repr(app) == "<App/(1, 1) %s (queued=0) [S]>" % id
