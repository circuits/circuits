#!/usr/bin/env python

import sys

from circuits import Component, handler
from circuits.io import File
from circuits.net.events import connect, write
from circuits.net.sockets import TCPClient


class Telnet(Component):

    channel = "telnet"

    def init(self, host, port):
        self.host = host
        self.port = port

        TCPClient(channel=self.channel).register(self)
        File(sys.stdin, channel="stdin").register(self)

    def ready(self, socket):
        self.fire(connect(self.host, self.port))

    def read(self, data):
        print(data.strip())

    @handler("read", channel="stdin")
    def read_user_input(self, data):
        self.fire(write(data))


host = sys.argv[1]
port = int(sys.argv[2])

Telnet(host, port).run()
