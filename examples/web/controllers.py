#!/usr/bin/env python

from os import path

from circuits.web import Server, Controller, Logger


class Root(Controller):

    def index(self):
        from circuits.tools import graph
        graph(self.root)
        return self.serve_file(path.abspath("Server.png"))

(Server(("0.0.0.0", 8000)) + Root() + Logger()).run()
