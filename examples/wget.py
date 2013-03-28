#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""wget Example

A basic wget-like clone that asynchronously connections
a remote web server requesting a given resource.
"""

import sys

from circuits import Component
from circuits.web.client import Client, Request


class WebClient(Component):

    def init(self, url):
        self.url = url

        Client().register(self)

    def ready(self, *args):
        self.fire(Request("GET", self.url))

    def response(self, response):
        print(response.read())
        raise SystemExit(0)

WebClient(sys.argv[1]).run()
