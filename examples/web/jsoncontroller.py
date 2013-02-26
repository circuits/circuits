#!/usr/bin/env python

from circuits.web import Server, JSONController


class Root(JSONController):

    def index(self):
        return {"success": True, "message": "Hello World!"}

(Server(8000) + Root()).run()
