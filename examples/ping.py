#!/usr/bin/env python
"""Clone of the standard UNIX "ping" command.

This example shows how you can utilize some of the buitlin I/O components
in circuits to write a very simple clone of the standard UNIX "ping" command.
This example merely wraps the standard UNIX "/usr/bin/ping" command in a subprocess
using the ``circuits.io.Process`` Component for Asyncchronous I/O communications with
the process.
"""
import sys

from circuits import Component, Debugger
from circuits.io import Process, stdout, write


class Ping(Component):

    # This adds the already instantiated stdout instnace
    stdout = stdout

    def init(self, host):
        self.p = Process(["/bin/ping", host]).register(self)
        self.p.start()

    def read(self, data):
        """read Event Handler

        This is fired by the File Component when there is data to be read
        from the underlying file that was opened.
        """

        self.fire(write(data), stdout)


# Start and "run" the system.
app = Ping(sys.argv[1])
Debugger().register(app)
app.run()
