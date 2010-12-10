#!/usr/bin/env python

from time import sleep

import py
py.test.skip("XXX: Not passing...")

from circuits import Event, Component, Manager

class Hello(Event):
    """Hello Event"""

class App(Component):

    def hello(self):
        return "Hello World!"

def test():
    m = Manager()
    m.start()

    app = App()
    app.start(link=m, process=True)

    x = m.push(Hello())
    sleep(1)

    s = str(x)
    assert s == "Hello World!"
