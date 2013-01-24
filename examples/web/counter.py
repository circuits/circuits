#!/usr/bin/env python

from StringIO import StringIO
from uuid import uuid4 as uuid

from circuits import handler
from circuits.io import File, Write, Close
from circuits.web import Server, Controller


class Root(Controller):

    def index(self):
        f = File("counter.txt", "r", channel=uuid()).register(self)
        yield self.wait("ready", f.channel)

        buffer = StringIO()

        def on_read(self, data):
            buffer.write(data)

        on_read_handler = self.addHandler(
            handler("read", channel=f.channel)(
                on_read
            )
        )

        #yield self.wait("opened", f.channel)
        yield self.wait("eof", f.channel)

        self.removeHandler(on_read_handler)

        try:
            n = int(buffer.getvalue()) + 1
        except ValueError:
            n = 1

        f.unregister()
        yield self.wait("unregistered", f.channel)

        f = File("counter.txt", "w", channel=uuid()).register(self)
        yield self.wait("ready", f.channel)

        self.fire(Write("{0:d}".format(n)), f.channel)
        yield self.wait("write", f.channel)

        self.fire(Close(), f.channel)
        yield self.wait("closed", f.channel)

        yield "You are visitor: {0:d}".format(n)


from circuits import Debugger
(Server(("0.0.0.0", 8000)) + Root() + Debugger()).run()
