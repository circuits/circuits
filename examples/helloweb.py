#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Web Hello

A simple example web server/application displaying "Hello World"
to the user's browser. This example demonstrates how to build a
simple but complete web server and application using circuits.
"""

import psyco; psyco.full()

from circuits import Component
from circuits.web import BaseServer

class Root(Component):

    def request(self, request, response):
        return "Hello World!"

def main():
    server = BaseServer(8000)
    server += Root()
    server.run()

if __name__ == "__main__":
    main()
