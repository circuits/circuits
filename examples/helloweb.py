#!/usr/bin/env python

from circuits import Component
from circuits.web import BaseServer

class Root(Component):

    def request(self, request, response):
        return "Hello World!"

(BaseServer(8000) + Root()).run()
