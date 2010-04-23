#!/usr/bin/env python

import py

from circuits import handler, Event, Component

class Test(Event):
    """Test Event"""

class App(Component):

    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        self.addHandler(handler("test")(self._test))

        self._event = None

    def _test(self, event, *args, **kwargs):
        self._event = event

def test():
    py.test.skip("FIXME: This feature is broken until furtner notice.")
    app = App()

    e = Test()
    app.push(e)
    app.flush()

    assert app._event == e
