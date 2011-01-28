#!/usr/bin/python -i

import os

import py

from circuits.net.sockets import Pipe
from circuits import Event, Component, Bridge

class Hello(Event):
    """Hello Event"""

class App(Component):

    def hello(self):
        return "Hello from %d" % os.getpid()

def test():
    # Our communication transport
    a, b = Pipe()

    # 1st App (process)
    p = App()
    Bridge(p, socket=a)
    p.start(process=True)

    # 2nd App
    app = App()
    Bridge(app, socket=b)
    app.start()

    pid = os.getpid()
    e = Hello()
    assert e.future == False
    x = app.push(e)

    py.test.wait_for(e, "future", True)
    assert e.future == True

    def test(obj, attr):
        return isinstance(obj._value, list)

    py.test.wait_for(x, None, test)

    assert x[0] == "Hello from %s" % pid
    assert x[1].startswith("Hello from")
    assert not x[0]  == x[1]
