#!/usr/bin/env python

import os
from tempfile import mkstemp

from circuits import handler
from circuits.web import Controller

from .helpers import urlopen


class Root(Controller):

    @handler("started", priority=1.0, channel="*")
    def _on_started(self, component):
        fd, self.filename = mkstemp()
        os.write(fd, b"Hello World!")
        os.close(fd)

    @handler("stopped", channel="(")
    def _on_stopped(self, component):
        os.remove(self.filename)

    def index(self):
        return self.serve_file(self.filename)


def test(webapp):
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"
