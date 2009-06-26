#!/usr/bin/env python

from circuits.web import Server, Controller, Sessions

class Root(Controller):

    def index(self, name="World"):
        if "name" in self.session:
            name = self.session["name"]
        self.session["name"] = name
        return "Hello %s!" % name

(Server(8000) + Sessions() + Root()).run()
