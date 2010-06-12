#!/usr/bin/env python

from circuits import Event, Component

class Test(Event):
    """Test Event"""

class App(Component):

    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        self.addHandler(self._test, "test")
        self.addHandler(self._test_target, "test", target="foo")

        self._event = None

    def _test(self, event, *args, **kwargs):
        self._event = event

    def _test_target(self, event, *args, **kwargs):
        self._event = event

def test():
    app = App()

    e = Test()
    app.push(e)
    app.flush()

    assert app._event == e

def test_target():
    app = App()

    e = Test()
    app.push(e, target="foo")
    app.flush()

    assert app._event == e
