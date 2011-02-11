#!/usr/bin/env python

import pytest

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

    assert pytest.wait_for(x, "result", True)
    s = str(x)
    assert s == "Hello World!"

    m.stop()
    app.stop()
