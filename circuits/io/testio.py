#!/usr/bin/env python

from circuits.io import *
from circuits import handler, Component, Debugger

class Test(Component):

    @handler("read", target="stdin")
    def read(self, data):
        stdout.write(data)

(Test() + stdin + stdout +  Debugger()).run()
