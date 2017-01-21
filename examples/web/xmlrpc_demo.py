#!/usr/bin/env python
from circuits import Component
from circuits.web import XMLRPC, Logger, Server


class Test(Component):

    def foo(self, a, b, c):
        return a, b, c


app = Server(("0.0.0.0", 8000))
Logger().register(app)
XMLRPC().register(app)
Test().register(app)
app.run()
