#!/usr/bin/env python

from types import ListType

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

    def exception(self, etype, evalue, etraceback, handler=None):
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

    app.push(Test())
    while app:
        app.flush()

    assert app.etype == NameError
    py.test.raises(NameError, lambda e: reraise(e), app.evalue)
    assert type(app.etraceback) is ListType
    assert app.handler == app.test
