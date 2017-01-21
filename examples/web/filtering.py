#!/usr/bin/env python
"""Filtering

A simple example showing how to intercept and potentially filter requests.
This example demonstrates how you could intercept the response before it goes
out changing the response's content into ALL UPPER CASE!
"""
from circuits import Component, handler
from circuits.web import Controller, Server


class Upper(Component):

    channel = "web"  # By default all web related events
    # go to the "web" channel.

    @handler("response", priority=1.0)
    def _on_response(self, response):
        """Response Handler

        Here we set the priority slightly higher than the default response
        handler in circutis.web (0.0) so that can we do something about the
        response before it finally goes out to the client.

        Here's we're simply modifying the response body by changing the content
        into ALL UPPERCASE!
        """

        response.body = "".join(response.body).upper()


class Root(Controller):

    def index(self):
        """Request Handler

        Our normal request handler simply returning
        "Hello World!" as the response.
        """

        return "Hello World!"


app = Server(("0.0.0.0", 8000))
Upper().register(app)
Root().register(app)
app.run()
