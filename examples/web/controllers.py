#!/usr/bin/env python

from circuits.web import Server, Controller, Logger

class Root(Controller):

    def index(self):
        agent = self.request.headers["User-Agent"]
        if "iPad" in agent:
            return "Hello iPad!"
        else:
            return "Hello World!"

(Server(("0.0.0.0", 8000)) + Root() + Logger()).run()
