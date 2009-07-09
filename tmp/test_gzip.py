#!/usr/bin/env python

from circuits import handler, Component, Debugger
from circuits.web.tools import gzip

class Gzip(Component):

    @handler("response", priority=1.0)
    def response(self, event, response):
        print "Gzipping response..."
        event[0] = response = gzip(response)
        print type(response.body)

from circuits.web import Server, Controller, Logger

class Root(Controller):

    def index(self):
        return "Hello World!"

(Server(("0.0.0.0", 8000))
        + Debugger()
        + Logger()
        + Gzip()
        + Root()).run()
