#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) UDP Client

A trivial simple example of using circuits to build a simple
UDP Socket Client.

This example demonstrates:
    * Basic Component creation.
    * Basic Event handling.
    * Basic Networking

This example makes use of:
    * Component
    * Event
    * Manager
    * net.sockets.UDPClient
"""

import sys

from circuits import handler
from circuits.io import stdin
from circuits.net.sockets import UDPClient


class Client(UDPClient):

    def __init__(self, target):
        super(Client, self).__init__(0)

        self._target = target

    def read(self, address, data):
        print "%r: %r" % (address, data.strip())

    @handler("read", channel="stdin")
    def stdin_read(self, data):
        self.write(self._target, data)


target = sys.argv[1].split(":")
target = target[0], int(target[1])

(Client(target) + stdin).run()
