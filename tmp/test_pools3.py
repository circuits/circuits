#!/usr/bin/env python

import sys
from time import sleep

from circuits import future, Pool
from circuits import Component, Event

class Test(Event):
    """Test Event"""

class App(Component):

    def __init__(self, N):
        super(App, self).__init__()

        Pool(min=10, max=20).register(self)

        self.N = N
        self.n = 0

    def __tick__(self):
        if self.n == self.N:
            raise SystemExit, 0
        print "."

    def started(self, component, mode):
        for i in xrange(self.N):
            v = self.push(Test())
            v.onSet = "value_changed", self

    def value_changed(self, value):
        self.n += 1
        print value

    @future()
    def test(self):
        sleep(5)
        return True
        #a = 0
        #i = 0
        #while i < 100000:
        #    a += (a + 1)
        #    i += 1
        #return a

if len(sys.argv) == 2:
    N = int(sys.argv[1])
else:
    N = 10

App(N).run()
