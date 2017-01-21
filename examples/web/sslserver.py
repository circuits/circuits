#!/usr/bin/env python
from circuits import Debugger
from circuits.web import Controller, Server


class Root(Controller):

    def index(self):
        return "Hello World!"


app = Server(("0.0.0.0", 8443), secure=True, certfile="cert.pem")
Debugger().register(app)
Root().register(app)
app.run()
