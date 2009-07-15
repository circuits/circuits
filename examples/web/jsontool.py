#!/usr/bin/env python

from json import dumps

from circuits.web import Server, Controller

def json(f):
    def wrapper(self, *args, **kwargs):
        return dumps(f(self, *args, **kwargs))
    return wrapper

class Root(Controller):

    @json
    def getrange(self, limit=4):
        return range(int(limit))

(Server(8000) + Root()).run()
