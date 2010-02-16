#!/usr/bin/env python

import os
import sys

from circuits import Component
from circuits.app import Daemon

class App(Component):

    def __init__(self, pidfile):
        super(App, self).__init__()

        Daemon(pidfile, stderr="/tmp/app.log").register(self)

def main():
    pidfile = os.path.abspath(sys.argv[1])
    app = App(pidfile)
    app.run()

if __name__ == "__main__":
    main()
