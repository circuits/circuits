#!/usr/bin/env python

from circuits import Event, Component

class Test(Event):
    """Test Event"""

class App(Component):

    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        self.addHandler(self._test, "test")

        self._event = None

    def _test(self, event, *args, **kwargs):
        self._event = event

def test():
    app = App()

    e = Test()
    app.push(e)
    app.flush()

    assert app._event == e
