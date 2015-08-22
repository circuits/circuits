#!/usr/bin/env python

from circuits.web import Server, Controller


class Root(Controller):

    def index(self):
        return "Hello World!"


app = Server(("0.0.0.0", 8443), secure=True, certfile="cert.pem")
from circuits import Debugger
Debugger().register(app)
Root().register(app)
app.run()
