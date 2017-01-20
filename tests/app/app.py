#!/usr/bin/env python
import sys
from os.path import abspath

from circuits import Component
from circuits.app import Daemon

try:
    from coverage import coverage
    HAS_COVERAGE = True
except ImportError:
    HAS_COVERAGE = False


class App(Component):

    def init(self, pidfile):
        self.pidfile = pidfile

    def started(self, *args):
        Daemon(self.pidfile).register(self)

    def prepare_unregister(self, *args):
        return


def main():
    if HAS_COVERAGE:
        _coverage = coverage(data_suffix=True)
        _coverage.start()

    args = iter(sys.argv)
    next(args)  # executable

    pidfile = next(args)  # pidfile

    pidfile = abspath(pidfile)

    App(pidfile).run()

    if HAS_COVERAGE:
        _coverage.stop()
        _coverage.save()


if __name__ == "__main__":
    main()
