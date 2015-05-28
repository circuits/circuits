#!/usr/bin/env python

import sys

from circuits import Component


class App(Component):

    def started(self, *args):
        raise SystemExit(int(sys.argv[1]))


def main():
    App().run()


if __name__ == "__main__":
    main()
