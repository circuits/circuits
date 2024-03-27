"""
Component Repr Tests

Test Component's representation string.
"""

import os
from threading import current_thread

from circuits import Component, Event


class App(Component):
    def test(self, event, *args, **kwargs):
        pass


class test(Event):
    pass


def test_main():
    id = f'{os.getpid()}:{current_thread().name}'
    app = App()

    assert repr(app) == '<App/* %s (queued=0) [S]>' % id

    app.fire(test())
    assert repr(app) == '<App/* %s (queued=1) [S]>' % id

    app.flush()
    assert repr(app) == '<App/* %s (queued=0) [S]>' % id


def test_non_str_channel():
    id = f'{os.getpid()}:{current_thread().name}'
    app = App(channel=(1, 1))

    assert repr(app) == '<App/(1, 1) %s (queued=0) [S]>' % id

    app.fire(test())
    assert repr(app) == '<App/(1, 1) %s (queued=1) [S]>' % id

    app.flush()
    assert repr(app) == '<App/(1, 1) %s (queued=0) [S]>' % id
