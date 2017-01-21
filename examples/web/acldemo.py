#!/usr/bin/env python
from circuits import Component, handler
from circuits.web import Controller, Server
from circuits.web.errors import Forbidden


class ACL(Component):

    allowed = ["127.0.0.1"]

    @handler("request", priority=1.0)
    def on_request(self, event, request, response):
        """Filter Requests applying IP based Authorization

        Filter any incoming requests at a higher priority than the
        default dispatcher and apply IP based Authorization returning
        a 403 Forbidden response if the Remote IP Address does not
        match the allowed set.
        """

        if request.remote.ip not in self.allowed:
            event.stop()
            return Forbidden(request, response)


class Root(Controller):

    def index(self):
        return "Hello World!"


app = Server(("0.0.0.0", 8000))
ACL().register(app)
Root().register(app)
app.run()
