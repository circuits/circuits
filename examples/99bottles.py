#!/usr/bin/env python

import sys

from circuits.io import File
from circuits import Component
from circuits.net.protocols import LP

class Tail(Component):

    def init(self, filename):
        (File(filename, "r", autoclose=False) + LP()).register(self).seek(0, 2)

class Grep(Component):

    def init(self, pattern):
        self.pattern = pattern

    def line(self, line):
        if self.pattern in line:
            print line

(Tail(sys.argv[1]) + Grep(sys.argv[2])).run()
