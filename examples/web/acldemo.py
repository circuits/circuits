#!/usr/bin/env python

from circuits import handler, Component
from circuits.web.errors import Forbidden
from circuits.web import Server, Controller

class ACL(Component):

    allowed = ["127.0.0.1"]

    @handler("request", filter=True)
    def on_request(self, request, response):
        if not request.remote.ip in self.allowed:
            return Forbidden(request, response)

class Root(Controller):

    def index(self):
        return "Hello World!"

(Server(("0.0.0.0", 8000)) + ACL() + Root()).run()
