#!/usr/bin/env python
"""Clone of the standard UNIX "tail" command.

This example shows how you can utilize some of the buitlin I/O components
in circuits to write a very simple clone of the standard UNIX "tail" command.
"""
import sys

from circuits import Component, Debugger
from circuits.io import File, Write, stdout


class Tail(Component):

    # Shorthand for declaring a compoent to be a part of this component.
    stdout = stdout

    def init(self, filename):
        """Initialize Tail Component

        Using the convenience ``init`` method we simply register a ``File``
        Component as part of our ``Tail`` Component and ask it to seek to
        the end of the file.
        """

        File(filename, "r", autoclose=False).register(self).seek(0, 2)

    def read(self, data):
        """Read Event Handler

        This event is triggered by the underlying ``File`` Component for
        when there is data to be processed. Here we simply fire a ``Write``
        event and target the ``stdout`` component instance that is a part of
        our system -- thus writing the contents of the file we read out
        to standard output.
        """

        self.fire(Write(data), self.stdout)


# Setup and run the system.
(Tail(sys.argv[1]) + Debugger()).run()
