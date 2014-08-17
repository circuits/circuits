#!/usr/bin/env python


from sys import argv
from os.path import abspath


try:
    from coverage import coverage
    HAS_COVERAGE = True
except ImportError:
    HAS_COVERAGE = False


from circuits import Component
from circuits.app import Daemon


class App(Component):

    def init(self, pidfile, **kwargs):
        Daemon(pidfile, **kwargs).register(self)

    def prepare_unregister(self, *args):
        return


def main():
    if HAS_COVERAGE:
        _coverage = coverage(data_suffix=True)
        _coverage.start()

    pidfile = abspath(argv[1])

    app = App(pidfile)

    app.run()

    if HAS_COVERAGE:
        _coverage.stop()
        _coverage.save()


if __name__ == "__main__":
    main()
