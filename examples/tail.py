#!/usr/bin/env python

import sys
from circuits import Component, Debugger
from circuits.io import stdout, File, Write

class Tail(Component):

    stdout = stdout

    def __init__(self, filename):
        super(Tail, self).__init__()
        File(filename, "r", autoclose=False).register(self).seek(0, 2)

    def read(self, data):
        self.fire(Write(data), target=self.stdout)

(Tail(sys.argv[1]) + Debugger()).run()
