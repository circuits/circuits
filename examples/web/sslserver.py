#!/usr/bin/env python

from circuits.web import Server, Controller

class Root(Controller):

    def index(self):
        return "Hello World!"

(Server(8000, ssl=True, certfile="cert.pem") + Root()).run()
