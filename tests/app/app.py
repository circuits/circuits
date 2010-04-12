#!/usr/bin/env python

import os
import sys

from coverage import coverage

from circuits import Component
from circuits.app import Daemon

class App(Component):

    def __init__(self, pidfile):
        super(App, self).__init__()

        Daemon(pidfile, stderr="/tmp/app.log").register(self)

def main():
    _coverage = coverage(data_suffix=True)
    _coverage.start()

    pidfile = os.path.abspath(sys.argv[1])
    app = App(pidfile)
    app.run()

    _coverage.stop()
    _coverage.save()

if __name__ == "__main__":
    main()
