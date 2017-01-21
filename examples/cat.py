#!/usr/bin/env python
"""Clone of the standard UNIX "cat" command.

This example shows how you can utilize some of the buitlin I/O components
in circuits to write a very simple clone of the standard UNIX "cat" command.
"""
import sys

from circuits.io import File, stdout, write


class Cat(File):

    # This adds the already instantiated stdout instnace
    stdout = stdout

    def read(self, data):
        """Read Event Handler

        This is fired by the File Component when there is data to be read
        from the underlying file that was opened.
        """

        self.fire(write(data), stdout)

    def eof(self):
        """End Of File Event

        This is fired by the File Component when the underlying input file
        has been exhcuasted.
        """

        raise SystemExit(0)


# Start and "run" the system.
Cat(sys.argv[1]).run()
