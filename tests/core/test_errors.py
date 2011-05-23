#!/usr/bin/env python

import py

from circuits import Event, Component

class Test(Event):
    """Test Event"""

class App(Component):

    def __init__(self):
        super(App, self).__init__()

        self.etype = None
        self.evalue = None
        self.etraceback = None
        self.handler = None

    def test(self):
        return x

    def error(self, etype, evalue, etraceback, handler=None):
        self.etype = etype
        self.evalue = evalue
        self.etraceback = etraceback
        self.handler = handler

def reraise(e):
    raise e

def test():
    app = App()
    while app:
        app.flush()

    app.fire(Test())
    while app:
        app.flush()

    assert app.etype == NameError
    py.test.raises(NameError, lambda e: reraise(e), app.evalue)
    assert isinstance(app.etraceback, list)
    assert app.handler == app.test
