#!/usr/bin/env python

import os
import sys

from circuits import Component
from circuits.app import Daemon

class App(Component):

    def __init__(self, pidfile, signalfile):
        super(App, self).__init__()

        self.pidfile = pidfile
        self.signalfile = signalfile

        Daemon(self.pidfile).register(self)

    def signal(self, signal, stack):
        f = open(self.signalfile, "w")
        f.write(str(signal))
        f.close()

def main():
    pidfile = os.path.abspath(sys.argv[1])
    signalfile = os.path.abspath(sys.argv[2])
    App(pidfile, signalfile).run()

if __name__ == "__main__":
    main()
