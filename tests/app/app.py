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
    def init(self, pidfile) -> None:
        self.pidfile = pidfile

    def started(self, *args) -> None:
        Daemon(self.pidfile).register(self)

    def prepare_unregister(self, *args) -> None:
        return


def main() -> None:
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


if __name__ == '__main__':
    main()
