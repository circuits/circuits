#!/usr/bin/env python
"""Simple Serial Example

This example shows how to use the ``circuits.io.Serial`` Component
to access serial data. This example simply echos back what it receives
on the serial port.

.. warning:: This example is currently untested.
"""
from circuits import Component, Debugger, handler
from circuits.io import Serial
from circuits.io.events import write


class EchoSerial(Component):

    def init(self, port):
        Serial(port).register(self)

    @handler("read")
    def on_read(self, data):
        """Read Event Handler

        This is fired by the underlying Serial Component when there has been
        new data read from the serial port.
        """

        self.fire(write(data))


# Start and "run" the system.
# Connect to /dev/ttyS0
app = EchoSerial("/dev/ttyS0")
Debugger().register(app)
app.run()
