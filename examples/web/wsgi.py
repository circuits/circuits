#!/usr/bin/env python

from circuits.web.wsgi import Gateway
from circuits.web import Controller, Server


def foo(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/plain")])
    return ["Foo!"]


class Root(Controller):
    """App Rot"""

    def index(self):
        return "Hello World!"


app = Server(("0.0.0.0", 10000))
Root().register(app)
Gateway({"/foo": foo}).register(app)
app.run()
