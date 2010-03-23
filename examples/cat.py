#!/usr/bin/env python

import sys

from circuits import Component
from circuits.io import stdout, File, Write

class Cat(Component):

    def __init__(self, filename):
        super(Cat, self).__init__()

        stdout.register(self)

        self._file = File(filename, "r")
        self._file.register(self)

    def read(self, data):
        self.push(Write(data), target=stdout)

    def eof(self):
        raise SystemExit, 0

Cat(sys.argv[1]).run()
