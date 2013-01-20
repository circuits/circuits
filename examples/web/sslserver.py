#!/usr/bin/env python

from circuits.web import Server, Controller


class Root(Controller):

    def index(self):
        return "Hello World!"


(Server(("localhost", 8000), secure=True, certfile="cert.pem") + Root()).run()
