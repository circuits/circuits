#!/usr/bin/env python

import os
from urllib2 import urlopen
from tempfile import mkstemp

from circuits import handler
from circuits.web import Controller

class Root(Controller):

    @handler("started", priority=1.0, target="*")
    def _on_started(self, component, mode):
        fd, self.filename = mkstemp()
        os.write(fd, "Hello World!")
        os.close(fd)

    @handler("stopped", target="(")
    def _on_stopped(self, component):
        os.remove(self.filename)

    def index(self):
        return self.serve_file(self.filename)

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s  == "Hello World!"
