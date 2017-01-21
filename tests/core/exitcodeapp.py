#!/usr/bin/env python
import sys

from circuits import Component


class App(Component):

    def started(self, *args):
        try:
            code = int(sys.argv[1])
        except ValueError:
            code = sys.argv[1]

        raise SystemExit(code)


def main():
    App().run()


if __name__ == "__main__":
    main()
