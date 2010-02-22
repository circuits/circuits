# Module:   test_manager_repr
# Date:     23rd February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Manager Repr Tests

Test Manager's representation string.
"""

from circuits import Event, Component, Manager

class App(Component):

    def test(self, event, *args, **kwargs):
        pass

def test():
    m = Manager()
    assert repr(m) == "<Manager (queued=0, channels=0, handlers=0) [S]>"

    app = App()
    app.register(m)
    assert repr(m) == "<Manager (queued=1, channels=1, handlers=1) [S]>"

    m.flush()
    assert repr(m) == "<Manager (queued=0, channels=1, handlers=1) [S]>"

    m.push(Event(), "test")
    assert repr(m) == "<Manager (queued=1, channels=1, handlers=1) [S]>"

    m.flush()
    assert repr(m) == "<Manager (queued=0, channels=1, handlers=1) [S]>"

    app.unregister()
    assert repr(m) == "<Manager (queued=1, channels=0, handlers=0) [S]>"

    m.flush()
    assert repr(m) == "<Manager (queued=0, channels=0, handlers=0) [S]>"
