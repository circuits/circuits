#!/usr/bin/env python
from circuits.web import Controller, Server, Sessions


class Root(Controller):

    def index(self, name="World"):
        if "name" in self.session:
            name = self.session["name"]
        self.session["name"] = name
        return "Hello %s!" % name


app = Server(("0.0.0.0", 8000))
Sessions().register(app)
Root().register(app)
app.run()
