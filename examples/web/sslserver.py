#!/usr/bin/env python

from circuits.web import Server, Controller


class Root(Controller):

    def index(self):
        return "Hello World!"


from circuits import Debugger
(
    Server(("localhost", 9000), secure=True, certfile="cert.pem") +
    Debugger() +
    Root()
).run()
