#!/usr/bin/env python

from circuits.web import Server, JSONController


class Root(JSONController):

    def index(self):
        return {"success": True, "message": "Hello World!"}

app = Server(("0.0.0.0", 8000))
Root().register(app)
app.run()
