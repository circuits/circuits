#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Comet Examples with circuits.web"""

import os
from subprocess import Popen, PIPE

from circuits.io import File
from circuits import Component
from circuits.web.events import Write
from circuits.web import Server, Controller, Logger

class Command(Component):

    channel = "cmd"

    def __init__(self, request, response, command, channel=channel):
        super(Command, self).__init__(channel=channel)

        self.request = request
        self.response = response
        self.command = command

        self.p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE,
                close_fds=True, preexec_fn=os.setsid)
        self.stdout = File(self.p.stdout, channel=channel)
        self.stdout.register(self)

    def read(self, data):
        self.push(Write(self.response.sock, data), "write", "server")

class Comet(Controller):

    def index(self):
        return "Hello World!"

    def ping(self, host):
        self.response.headers["Content-Type"] = "text/plain"
        self.response.close = False
        Command(self.request, self.response, "ping %s" % host).register(self)
        return True

(Server(10000) + Logger() + Comet()).run()
