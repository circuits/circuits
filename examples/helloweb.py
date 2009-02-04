#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Web Hello

A simple example web server/application displaying "Hello World"
to the user's browser. This example demonstrates how to build a
simple but complete web server and application using circuits.
"""

from circuits import Component
from circuits.web import BaseServer, Response

class HelloWorld(Component):
    """HelloWorld Component

    A Component that will listen to "index" Events and return an appropiate
    HTTP Response with the message "Hello Worl!".
    """

    def request(self, request, response, *args, **kwargs):
        """Index Event Handler

        HTTP Request Handler that listens on the "index' channel which maps
        to http://localhost:8000/ When a Request is received, send back an
        appropiate HTTP Response with contens of the body being "Hello World!"
        """

        response.body = "Hello World!"
        self.send(Response(response), "response")

def main():
    server = BaseServer(8000)
    server += HelloWorld()
    server.run()

if __name__ == "__main__":
    main()
