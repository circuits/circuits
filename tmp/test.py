#!/usr/bin/env python

import re
from time import sleep

from circuits import Event, Component, Manager, Thread

SEEK_END = 2
BLOCKSIZE = 8192

LINESEP = re.compile("\r?\n")

def splitLines(s, buffer):
    lines = LINESEP.split(buffer + s)
    return lines[:-1], lines[-1]

class Follow(Thread):

    def __init__(self, fd):
        super(Follow, self).__init__()
        self.fd = fd
        self.fd.seek(0, SEEK_END)

    def stopped(self, manager):
        if not manager == self:
            self.stop()

    def run(self):
        while self.alive:
            data = self.fd.read(BLOCKSIZE)
            if data:
                self.push(Event(data), "read", self.channel)
                sleep(0.01)
            else:
                sleep(0.1)

class LineBuffer(Component):

    def __init__(self):
        super(LineBuffer, self).__init__()
        self._data = ""

    def read(self, data):
        lines, self._data = splitLines(data, self._data)
        for line in lines:
            self.push(Event(line), "line", self.channel)

class Grep(Component):

    def __init__(self, pattern):
        super(Grep, self).__init__()
        self._pattern = pattern

    def line(self, line):
        if self._pattern in line:
            print line

m = Manager()
f = Follow(file("/tmp/foo"))
f.register(m)
LineBuffer().register(m)
Grep("pants").register(m)

f.start()
m.run()
