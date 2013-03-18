#!/usr/bin/env python

from circuits import handler, Component
from circuits.web import Server, Controller


class Upper(Component):

    channel = "web"

    @handler("response", priority=1.0)
    def _on_response(self, response):
        """Filter Response and modify it

        Filter the outgoing Response and modify it turning the
        text of the body into uppercase.
        """

        response.body = "".join(response.body).upper()


class Root(Controller):

    def index(self):
        return "Hello World!"

(Server(9000) + Upper() + Root()).run()
