#!/usr/bin/env python
"""
wget Example

A basic wget-like clone that asynchronously connections
a remote web server requesting a given resource.
"""

import sys

from circuits import Component
from circuits.web.client import Client, request


class WebClient(Component):
    def init(self, url):
        self.url = url

        Client().register(self)

    def ready(self, *args):
        self.fire(request('GET', self.url))

    def response(self, response):
        print(f'{response.status:d} {response.reason:s}')
        print(
            '\n'.join(f'{k:s}: {v:s}' for k, v in response.headers.items()),
        )
        print(response.read())
        raise SystemExit(0)


WebClient(sys.argv[1]).run()
