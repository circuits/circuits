#!/usr/bin/env python

from circuits import Debugger
from circuits.web import Server, Controller, Response

class Root(Controller):

    def index(self):
        self.response.body = "Hello World!"
        self.push(Response(self.response), target="http")

(Server(8000) + Debugger() + Root()).run()
