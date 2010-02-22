# Module:   test_component_repr
# Date:     23rd February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Component Repr Tests

Test Component's representation string.
"""

from circuits import Event, Component

class App(Component):

    def test(self, event, *args, **kwargs):
        pass

def test():
    app = App()
    assert repr(app) == "<App/* (queued=0, channels=1, handlers=1) [S]>"

    app.flush()
    assert repr(app) == "<App/* (queued=0, channels=1, handlers=1) [S]>"

    app.push(Event(), "test")
    assert repr(app) == "<App/* (queued=1, channels=1, handlers=1) [S]>"

    app.flush()
    assert repr(app) == "<App/* (queued=0, channels=1, handlers=1) [S]>"

    app.unregister()
    assert repr(app) == "<App/* (queued=1, channels=0, handlers=0) [S]>"

    app.flush()
    assert repr(app) == "<App/* (queued=0, channels=0, handlers=0) [S]>"
