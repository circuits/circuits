#!/usr/bin/env python

from circuits import Component, Event


class Hello(Event):
    """Hello Event"""


class App(Component):

    def hello(self, event):
        print("Hello World!")
        event.stop()


    def started(self, event, component):
        event.stop()
        self.fire(Hello())
        raise SystemExit(0)

(App() + App()).run()
