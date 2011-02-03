#!/usr/bin/env python

from circuits import handler, Component
from circuits.web import Server, Controller

class Upper(Component):

    channel = "web"

    @handler("response", priority=1.0)
    def _on_response(self, response):
        response.body = "".join(response.body).upper()

class Root(Controller):

    def index(self):
        return "Hello World!"

(Server(8000) + Upper() + Root()).run()
