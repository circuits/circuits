#!/usr/bin/env python

from circuits.core.debugger import Debugger
from circuits.core.components import BaseComponent
from circuits.core.handlers import handler

class MyComponent(BaseComponent):

    def __init__(self):
        super(MyComponent, self).__init__()

        Debugger().register(self)

    @handler("started", channel="*")
    def _on_started(self, component):
        print "Start event detected"

MyComponent().run()
