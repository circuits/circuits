#!/usr/bin/env python

import os
from time import sleep
from urllib2 import urlopen

from circuits.web import Controller, Server
from circuits import  handler, Event, Component, Process

class Hello(Event):
    """Hello Event"""

class Root(Controller):

    def index(self):
        return self.push(Hello(os.getpid()))

class MyProcess(Process):

    @handler("hello", target="*")
    def hello(self, pid):
        return "Hello %d i'm %d" % (pid, os.getpid())

    def run(self):
        while self.running:
            sleep(1)

def test(webapp):
    p = MyProcess(webapp)
    p.start()

    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello %d i'm %d" % (os.getpid(), p._process.pid)
