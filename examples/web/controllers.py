#!/usr/bin/env python
from circuits import Debugger
from circuits.web import Controller, Server, Static


class Root(Controller):

    def index(self):
        """Index Request Handler

        Controller(s) expose implicitly methods as request handlers.
        Request Handlers can still be customized by using the ``@expose``
        decorator. For example exposing as a different path.
        """

        return "Hello World!"


app = Server(("0.0.0.0", 9000))
Debugger().register(app)
Static().register(app)
Root().register(app)
app.run()
