#!/usr/bin/env python
import os
import sys

from circuits import Component
from circuits.app import Daemon

code = eval(sys.argv[1])

class App(Component):
    def started(self, x):
        raise SystemExit(code)


def main():
    App().run()

if __name__ == "__main__":
    main()

