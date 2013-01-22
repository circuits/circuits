#!/usr/bin/env python

import gc

from circuits import Component, Event
from circuits.web import Controller, Server


class Hello(Event):
    """Hello Event"""


class App(Component):

    def hello(self):
        print("Hello World!")

    def started(self, component):
        self.fire(Hello())
        raise SystemExit(0)


class Root(Controller):

    def index(self):
        return "Hello World!"


old_count = len(gc.get_count())

#App().run()
(Server(8000) + Root()).run()

gc.collect()
new_count = len(gc.get_count())
diff_count = new_count - old_count

if diff_count > 0:
    print("Memory Leak Detected of {0:d} objects".format(diff_count))

    for obj in gc.get_objects():
        print("Object:", obj)
        print(" Referrers:")
        for ref in gc.get_referrer(obj):
            print("  ", ref)
else:
    print("OK")
