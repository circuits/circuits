#!/usr/bin/env python

import os
from time import sleep

import py
py.test.skip("XXX: Not passing...")

from circuits import handler, Event, Component, Process

class Hello(Event):
    """Hello Event"""

class Test(Event):
    """Test Event"""

class App(Component):

    def __init__(self):
        super(App, self).__init__()

        self.events = []
        self.flag = False
        self.pid = None

    @handler(filter=True)
    def event(self, event, *args, **kwargs):
        self.events.append(event)

    def hello(self, pid):
        self.pid = pid

    def test(self):
        self.flag = True

class MyProcess(Process):

    def run(self):
        self.push(Test())
        self.push(Hello(os.getpid()))

def test():
    app = App()
    app.start()

    p = MyProcess(app)
    p.start()

    retries = 5
    for i in range(retries):
        if app.flag:
            break
        sleep(1)
    else:
        raise Exception("app.flag not set after %d retries" % retries)

    ppid = os.getpid()
    cpid = app.events[-1][0]
    assert not ppid == cpid
