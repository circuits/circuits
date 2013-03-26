#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""wget Example

A basic wget-like clone that asynchronously connections
a remote web server requesting a given resource.
"""

import sys

from circuits import Component
from circuits.io import stdout, Write
from circuits.web.client import Client, Connect, Request


class WebClient(Component):

    channel = "client"

    stdout = stdout

    def init(self, url, channel=channel):
        self.url = url

        self.client = Client(url, channel=channel).register(self)

    def ready(self, client):
        self.fire(Connect())
        yield self.wait("connected")

        self.fire(Request("GET", self.url))
        yield self.wait("response")

        self.fire(Write(self.client.response.read()), stdout)

WebClient(sys.argv[1]).run()
