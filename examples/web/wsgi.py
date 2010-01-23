#!/usr/bin/env python

from circuits.web import wsgi
from circuits.web import BaseServer

def application(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/plain")])
    return ["Hello World!"]

(BaseServer(8000) + wsgi.Gateway(application)).run()
