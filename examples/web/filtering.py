#!/usr/bin/env python

from circuits import Component
from circuits.web import Server, Controller

class Upper(Component):

    channel = "http"

    def response(self, response):
        response.body = response.body.upper()

class Root(Controller):

    def index(self):
        return "Hello World!"

(Server(8000) + Upper() + Root()).run()
