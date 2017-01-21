#!/usr/bin/env python
from circuits import Component
from circuits.web import BaseServer


class Root(Component):

    def request(self, request, response):
        """Request Handler

        Using ``BaseServer`` provides no URL dispatching of any kind.
        Requests are handled by any event handler listening to
        ``Request`` events and must accept a (request, response)
        as arguments.
        """

        return "Hello World!"


app = BaseServer(("0.0.0.0", 8000))
Root().register(app)
app.run()
