#!/usr/bin/env python

from circuits.web import BaseServer
from circuits.web.wsgi import Gateway


def application(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/plain")])
    return ["Hello World!"]

app = BaseServer(("0.0.0.0", 8000))
Gateway(application).register(app)
app.run()
