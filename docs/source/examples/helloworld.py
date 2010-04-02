#!/usr/bin/env python

from circuits import Event, Component

class Hello(Event):
    """Hello Event"""

    end = "goodbye",

class App(Component):

    def started(self, component, mode):
        self.push(Hello())

    def hello(self):
        print "Hello World!"

    def goodbye(self, e, handler, v):
        print "Goodbye World!"
        print "Event:", e
        print "Handler", handler
        print "Return Value:", v
        raise SystemExit, 0

App().run()
