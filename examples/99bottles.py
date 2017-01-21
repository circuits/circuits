#!/usr/bin/env python
"""An implementation of the Python Concurrency Problem of 99 Bottles of Beer

See: http://wiki.python.org/moin/Concurrency/99Bottles
"""
from __future__ import print_function

import sys

from circuits import Component
from circuits.io import File
from circuits.protocols import Line


class Tail(Component):

    """A complex component which combines the ``File`` and ``LP``
    (Line Protoco) components together to implement similar functionality to
    the UNIX ``tail`` command.
    """

    def init(self, filename):
        """Initialize the Component.

        NB: This is automatically called after ``__new__`` and ``__init__``.
        """

        (File(filename, "r") + Line()).register(self)


class Grep(Component):

    """A simple component that simply listens for ``line`` events from the
    ``Tail`` component and performs a regular expression match against each
    line. If the line matches it is printed to standard output.
    """

    def init(self, pattern):
        self.pattern = pattern

    def line(self, line):
        """Line Event Handler"""

        line = line.decode("utf-8")

        if self.pattern in line:
            print(line)


# Configure and "run" the System.
app = Tail(sys.argv[1])
Grep(sys.argv[2]).register(app)
app.run()
