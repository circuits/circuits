#!/usr/bin/env python

import os
import sys

try:
    from coverage import coverage
    HAS_COVERAGE = True
except ImportError:
    HAS_COVERAGE = False

from circuits import Component
from circuits.app import Daemon

class App(Component):

    def __init__(self, pidfile):
        super(App, self).__init__()

        Daemon(pidfile).register(self)

def main():
    if HAS_COVERAGE:
        _coverage = coverage(data_suffix=True)
        _coverage.start()

    pidfile = os.path.abspath(sys.argv[1])
    app = App(pidfile)
    app.run()

    if HAS_COVERAGE:
        _coverage.stop()
        _coverage.save()

if __name__ == "__main__":
    main()
