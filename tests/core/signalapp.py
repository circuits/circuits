#!/usr/bin/env python

import os
import sys

from coverage import coverage

from circuits import Component
from circuits.app import Daemon

class App(Component):

    def __init__(self, pidfile, signalfile):
        super(App, self).__init__()

        self.pidfile = pidfile
        self.signalfile = signalfile

        Daemon(self.pidfile).register(self)

    def signal(self, signal, stack):
        with open(self.signalfile, "w") as f:
            f.write(str(signal))

def main():
    _coverage = coverage(data_suffix=True)
    _coverage.start()

    pidfile = os.path.abspath(sys.argv[1])
    signalfile = os.path.abspath(sys.argv[2])
    App(pidfile, signalfile).run()

    _coverage.stop()
    _coverage.save()

if __name__ == "__main__":
    main()
