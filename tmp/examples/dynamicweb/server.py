#!/usr/bin/env python

from circuits import Loader
from circuits.web import Server, Controller, Logger

class Root(Controller):

    loader = Loader(paths=["./plugins"])

    def index(self):
        return "Hello World!"

    def load(self, name):
        try:
            self.loader.load(name)
            return "OK"
        except:
            return "Failed"


(Server(("0.0.0.0", 8000)) + Root() + Logger()).run()
