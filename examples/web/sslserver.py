#!/usr/bin/env python

from circuits import Debugger
from circuits.web import Server, Controller

class Root(Controller):

    def index(self):
        return "Hello World!"

(Server(("localhost", 8000), ssl=True, certfile="cert.pem") + Debugger() + Root()).run()