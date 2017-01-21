#!/usr/bin/env python
import os
from tempfile import mkstemp

from circuits.web import Controller

from .helpers import urlopen


class Root(Controller):

    def __init__(self, *args, **kwargs):
        super(Root, self).__init__(self, *args, **kwargs)

        fd, self.filename = mkstemp()
        os.write(fd, b"Hello World!")
        os.close(fd)

    def __del__(self):
        os.remove(self.filename)

    def index(self):
        return self.serve_file(self.filename)


def test(webapp):
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"
