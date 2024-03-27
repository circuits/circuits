#!/usr/bin/env python
# curl -i http://localhost:8000/getrange?limit=8
from json import dumps

from circuits.web import Controller, Server


def json(f):
    def wrapper(self, *args, **kwargs):
        return dumps(f(self, *args, **kwargs))

    return wrapper


class Root(Controller):
    @json
    def getrange(self, limit=4):
        return list(range(int(limit)))


app = Server(('0.0.0.0', 8000))
Root().register(app)
app.run()
