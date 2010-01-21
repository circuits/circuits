#!/usr/bin/env python

from circuits.io import File
from circuits import Component, Debugger

import sys
import tty
import termios
from contextlib import contextmanager


@contextmanager
def restore_tty_settings(fd):
    old = termios.tcgetattr(fd)
    yield
    termios.tcsetattr(fd, termios.TCSADRAIN, old)

    
class Echo(Component):

    def read(self, data):
        if data.lower() == "q":
            raise SystemExit, 0
        else:
            sys.stdout.write(data)
            sys.stdout.flush()


def main():
    stdin = File("/dev/stdin", "r", bufsize=1)
    
    with restore_tty_settings(stdin._fd):
        tty.setraw(stdin._fd)
        (Echo() + stdin).run()


if __name__ == '__main__':
    main()
