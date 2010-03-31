#!/usr/bin/env python

from circuits import Event, Component

class Hello(Event):
    """Hello Event"""

class App(Component):

    def started(self, component, mode):
        self.push(Hello())

    def hello(self):
        print "Hello World!"
        raise SystemExit, 0

App().run()
