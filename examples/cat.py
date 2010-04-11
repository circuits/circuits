#!/usr/bin/env python

import sys

from circuits.io import stdout, File, Write

class Cat(File):

    def __init__(self, filename, mode="r"):
        super(Cat, self).__init__(filename, mode)

        stdout.register(self)

    def read(self, data):
        self.push(Write(data), target=stdout)

    def eof(self):
        raise SystemExit, 0

Cat(sys.argv[1]).run()
