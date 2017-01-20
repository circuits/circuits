#!/usr/bin/env python

from circuits.web import Controller, Server


class Root(Controller):

    def index(self):
        """Index Request Handler

        Controller(s) expose implicitly methods as request handlers.
        Request Handlers can still be customized by using the ``@expose``
        decorator. For example exposing as a different path.
        """

        return "Hello World!"

app = Server(("0.0.0.0", 8000))
Root().register(app)
app.run()
