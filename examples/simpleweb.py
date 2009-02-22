#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Simple Web Hello

Web-based Hello World example. This example is exactly the same as
the helloweb.py example, except that it tries to simplify things by
using more higher abstracted web components from the web components
library.
"""

import psyco; psyco.full()

from circuits import Debugger
from circuits.web import sessions
from circuits.web import Server, Controller

class Root(Controller):

    def index(self):
        return "Hello World!"

    def foo(self):
        return "Foobar"

    def hello(self, name=None):
        name = name or self.session.get("name", "anonymous")
        self.session["name"] = name

        print "name = %s" % name

        return "Hello %s" % name

(Server(8000) + Debugger(events=False) + sessions.Sessions() + Root()).run()
