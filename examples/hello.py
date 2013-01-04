#!/usr/bin/env python

from circuits import Component, Event


class Hello(Event):
    """Hello Event"""


class App(Component):

    def hello(self):
        print("Hello World!")

    def started(self, component):
        self.fire(Hello())
        self.stop()

App().run()
