#!/usr/bin/env python

from circuits import Loader
from circuits.web import Server, Controller, Logger

class Root(Controller):

    loader = Loader(paths=["./plugins"])

    def index(self):
        return "Hello World!"

    def load(self, name):
        try:
            result = self.loader.load(name)
            if result is not None:
                return "Successfully loaded %s" % name
            else:
                return "Failed to find %s" % name
        except:
            return "Failed to load %s" % name


(Server(("0.0.0.0", 8000)) + Root() + Logger()).run()
