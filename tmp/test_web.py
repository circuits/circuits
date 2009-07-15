#!/usr/bin/python

from circuits import Component, Debugger
from circuits.web import BaseServer

class Root(Component):

    channel = "web"

    def request(self, request, response):
        return "Hello World!"

(BaseServer(9000) + Debugger() + Root()).run()
