#!/usr/bin/env python

from circuits import Component
from circuits.web import BaseServer, Response

class Root(Component):

    def request(self, request, response):
        response.body = "Hello World!"
        self.push(Response(response))

(BaseServer(8000) + Root()).run()
