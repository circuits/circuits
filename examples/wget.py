#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""wget Example

A basic wget-like clone that asynchronously connections
a remote web server requesting a given resource.
"""

import sys

from circuits import Component
from circuits.io import stdout, Write
from circuits.web.client import Close, Client, Connect, Request


class WebClient(Component):

    stdout = stdout

    def init(self, url):
        self.url = url

        self.client = Client().register(self)

    def ready(self, client):
        self.fire(Request("GET", self.url))

    def response(self, response):
        self.fire(Write(response.read()), stdout)
        self.fire(Close())

    def disconnected(self):
        raise SystemExit(0)

WebClient(sys.argv[1]).run()
