# Module:   test_component_repr
# Date:     23rd February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Component Repr Tests

Test Component's representation string.
"""

import os

try:
    from threading import current_thread
except ImportError:
    from threading import currentThread as current_thread

from circuits import Event, Component

class App(Component):

    def test(self, event, *args, **kwargs):
        pass

def test():
    id = "%s:%s" % (os.getpid(), current_thread().getName())

    app = App()
    assert repr(app) == "<App/* %s (queued=0, channels=1, handlers=1) [S]>" % id

    app.flush()
    assert repr(app) == "<App/* %s (queued=0, channels=1, handlers=1) [S]>" % id

    app.push(Event(), "test")
    assert repr(app) == "<App/* %s (queued=1, channels=1, handlers=1) [S]>" % id

    app.flush()
    assert repr(app) == "<App/* %s (queued=0, channels=1, handlers=1) [S]>" % id

    app.unregister()
    assert repr(app) == "<App/* %s (queued=1, channels=0, handlers=0) [S]>" % id

    app.flush()
    assert repr(app) == "<App/* %s (queued=0, channels=0, handlers=0) [S]>" % id
