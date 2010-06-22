# Module:   test_manager_repr
# Date:     23rd February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Manager Repr Tests

Test Manager's representation string.
"""

import os

try:
    from threading import current_thread
except ImportError:
    from threading import currentThread

from circuits import Event, Component, Manager

class App(Component):

    def test(self, event, *args, **kwargs):
        pass

def test():
    id = "%s:%s" % (os.getpid(), current_thread().getName())

    m = Manager()
    assert repr(m) == "<Manager %s (queued=0, channels=0, handlers=0) [S]>" % id

    app = App()
    app.register(m)
    assert repr(m) == "<Manager %s (queued=1, channels=1, handlers=1) [S]>" % id

    m.flush()
    assert repr(m) == "<Manager %s (queued=0, channels=1, handlers=1) [S]>" % id

    m.push(Event(), "test")
    assert repr(m) == "<Manager %s (queued=1, channels=1, handlers=1) [S]>" % id

    m.flush()
    assert repr(m) == "<Manager %s (queued=0, channels=1, handlers=1) [S]>" % id

    app.unregister()
    assert repr(m) == "<Manager %s (queued=1, channels=0, handlers=0) [S]>" % id

    m.flush()
    assert repr(m) == "<Manager %s (queued=0, channels=0, handlers=0) [S]>" % id
