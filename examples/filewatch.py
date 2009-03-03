#!/usr/bin/env python

import sys
from time import sleep
from circuits import Component

class FileWatcher(Component):

    def __init__(self, filename):
        super(FileWatcher, self).__init__()

        self.filename = filename
        self.fp = open(self.filename, "r")

    def __tick__(self):
        self.fp.seek(self.fp.tell())
        for line in self.fp.readlines():
            sys.stdout.write(line) 
        sleep(0.1)

filewatcher = FileWatcher(sys.argv[1])
filewatcher.run()
