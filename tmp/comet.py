#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Comet Examples with circuits.web"""

import os
import signal
from subprocess import Popen, PIPE

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from circuits.io import File
from circuits.web.events import Stream
from circuits.tools import kill, graph, inspect
from circuits import handler, Event, Component, Debugger
from circuits.web import Server, Controller, Logger, Sessions

BUFFERING = 1
STREAMING = 2

class Kill(Event): pass

class Command(Component):

    channel = "cmd"

    def __init__(self, request, response, command, channel=channel):
        super(Command, self).__init__(channel=channel)

        self._request = request
        self._response = response
        self._command = command

        self._state = BUFFERING
        self._buffer = None

        self._p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE,
                close_fds=True, preexec_fn=os.setsid)
        self._stdout = File(self._p.stdout, channel=channel)
        self._stdout.register(self)

    @handler("disconnect", target="server")
    def disconnect(self, sock):
        if sock == self._request.sock:
            self.push(Kill(), target=self)

    @handler("response", target="http", priority=-1)
    def response(self, response):
        if response == self._response:
            self._state = STREAMING

    def kill(self):
        os.killpg(self._p.pid, signal.SIGINT)
        kill(self)

    def read(self, data):
        if self._state == BUFFERING:
            if self._buffer is None:
                self._buffer = StringIO()
            self._buffer.write(data)
        elif self._state == STREAMING:
            if self._buffer is not None:
                self._buffer.write(data)
                self._buffer.flush()
                data = self._buffer.getvalue()
                self._buffer = None
                self.push(Stream(self._response, data), target="http")
            else:
                self.push(Stream(self._response, data), target="http")

class Comet(Controller):

    def index(self):
        return "Hello World!"

    def ping(self, host):
        self.response.headers["Content-Type"] = "text/plain"
        self.response.stream = True
        sid = self.request.sid
        command = "ping %s" % host
        self += Command(self.request, self.response, command, channel=sid)
        return self.response

app = (Server(8000) + Sessions() + Logger() + Comet())
app.run()
