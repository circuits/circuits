#!/usr/bin/env python

"""Web Counter (Advanced)

This advanced example demonstrates how you might develop a very simple
web application that responded with "You are visito:r <n>" where <n>
is incremented for every visit.

This is done by reading from a file called "counter.txt" and reading a
simple single integer value, increments it and writing it back.

This is all done asynchronously using circuits ``File`` I/O Component
and taking advantage of circuits ``wait`` primitives enabling the use
of lightweight coperative coroutines in the request handlers.
"""

from StringIO import StringIO
from uuid import uuid4 as uuid

from circuits import handler
from circuits.io import File, Write, Close
from circuits.web import Server, Controller


class Root(Controller):

    def index(self):
        """Request Handler"""

        # Open the "counter.txt" file for reading.
        # Set a unique channel for the file and register it.
        f = File("counter.txt", "r", channel=uuid()).register(self)

        # Wait for the file to be ready
        yield self.wait("ready", f.channel)

        # In-memory buffer to store the file's contents
        buffer = StringIO()

        # Temporary event handler for the File's ``Read`` events
        def on_read(self, data):
            buffer.write(data)

        # Bind the ``on_read`` function as an event handler
        on_read_handler = self.addHandler(
            handler("read", channel=f.channel)(
                on_read
            )
        )

        # Wait until we see the ``EOF`` event
        yield self.wait("eof", f.channel)

        # Remove the temporary event handler
        self.removeHandler(on_read_handler)

        #
        # Parse the contents of the buffer as an integer
        #

        try:
            n = int(buffer.getvalue()) + 1
        except ValueError:
            n = 1

        # Unregister the File and wait until done
        f.unregister()
        yield self.wait("unregistered", f.channel)

        #
        # Similar set of sequences but this time we're writing
        #

        f = File("counter.txt", "w", channel=uuid()).register(self)
        yield self.wait("ready", f.channel)

        self.fire(Write("{0:d}".format(n)), f.channel)
        yield self.wait("write", f.channel)

        self.fire(Close(), f.channel)
        yield self.wait("closed", f.channel)

        # Finally return a response to the request
        yield "You are visitor: {0:d}".format(n)


(Server(("0.0.0.0", 9000)) + Root()).run()
