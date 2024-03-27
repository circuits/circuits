#!/usr/bin/env python
import locale
import os
import sys

from circuits import Component
from circuits.app import Daemon


try:
    from coverage import coverage

    HAS_COVERAGE = True
except ImportError:
    HAS_COVERAGE = False


class App(Component):
    def init(self, pidfile, signalfile) -> None:
        self.pidfile = pidfile
        self.signalfile = signalfile

        Daemon(self.pidfile).register(self)

    def signal(self, signal, stack) -> None:
        f = open(self.signalfile, 'w', encoding=locale.getpreferredencoding(False))
        f.write(str(signal))
        f.close()
        self.stop()


def main() -> None:
    if HAS_COVERAGE:
        _coverage = coverage(data_suffix=True)
        _coverage.start()

    pidfile = os.path.abspath(sys.argv[1])
    signalfile = os.path.abspath(sys.argv[2])
    App(pidfile, signalfile).run()

    if HAS_COVERAGE:
        _coverage.stop()
        _coverage.save()


if __name__ == '__main__':
    main()
