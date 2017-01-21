#!/usr/bin/env python
from circuits.web import Server
from circuits.web.controllers import BaseController, expose


class Root(BaseController):

    @expose("index")
    def index(self):
        """Index Request Handler

        BaseController(s) do not expose methods as request handlers.
        Request Handlers _must_ be exposed explicitly using the ``@expose``
        decorator.
        """

        return "Hello World!"


app = Server(("0.0.0.0", 8000))
Root().register(app)
app.run()
