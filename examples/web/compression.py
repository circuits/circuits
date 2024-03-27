#!/usr/bin/env python
# Examples:
# curl http://127.0.0.1:8000/ -i -H 'Accept-Encoding: gzip'
# curl http://127.0.0.1:8000/ -i -H 'Accept-Encoding: deflate'
# curl http://127.0.0.1:8000/ -i -H 'Accept-Encoding: identity'

from circuits import Component, Debugger, handler
from circuits.web import Server
from circuits.web.controllers import BaseController, expose
from circuits.web.tools import gzip


class Gzip(Component):
    @handler('response', priority=1.0)
    def compress_response(self, event, response):
        event[0] = gzip(response)


class Root(BaseController):
    @expose('index')
    def index(self):
        return 'Hello World! This is some test string which is compressed using gzip-4 if you want!'


app = Server(('0.0.0.0', 8000))
Root().register(app)
Gzip().register(app)
Debugger().register(app)
app.run()
