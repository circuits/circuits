#!/usr/bin/env python
# curl -i http://localhost:8000/foo/
from circuits.web import Controller, Server
from circuits.web.wsgi import Gateway


def foo(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Foo!']


class Root(Controller):
    """App Rot"""

    def index(self):
        return 'Hello World!'


app = Server(('0.0.0.0', 8000))
Root().register(app)
Gateway({'/foo': foo}).register(app)
app.run()
