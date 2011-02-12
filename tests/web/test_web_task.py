#!/usr/bin/env python

import os
from urllib2 import urlopen

import pytest

from circuits.core.manager import HAS_MULTIPROCESSING
if not HAS_MULTIPROCESSING:
    pytest.skip("Skip: No multiprocessing support")

from circuits.web import Controller
from circuits import Event, Component

class Hello(Event):
    """Hello Event"""

class Root(Controller):

    def index(self):
        return self.push(Hello(os.getpid()))

class Task(Component):

    def hello(self, pid):
        return "Hello %d i'm %d" % (pid, os.getpid())

def test(webapp):
    t = Task()
    t.start(link=webapp, process=True)
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello %d i'm %d" % (os.getpid(), t._task.pid)
    t.stop()
