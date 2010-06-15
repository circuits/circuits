#!/usr/bin/env python


import os
import signal
from StringIO import StringIO
from subprocess import Popen, PIPE

from circuits.io import File
from circuits.tools import kill
from circuits.web.events import Stream
from circuits import handler, Event, Component
from circuits.web import Server, Controller, Logger, Static, Sessions

BUFFERING = 1
STREAMING = 2

class Kill(Event): pass
class Input(Event): pass

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

        self._stdin = None
        if self._p.stdin is not None:
            self._stdin = File(self._p.stdin, channel="%s.stdin" % channel)
            self._stdin.register(self)

        self._stdout = File(self._p.stdout, channel="%s.stdout" % channel)
        self.addHandler(self._on_stdout_eof, "eof",
                target="%s.stdout" % channel)
        self.addHandler(self._on_stdout_read, "read",
                target="%s.stdout" % channel)
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

    def input(self, data):
        if self._stdin is not None:
            self.push(Write(data), target=self._stdin)

    def _on_stdout_eof(self):
        if self._buffer is not None:
            self._buffer.flush()
            data = self._buffer.getvalue()
            self.push(Stream(self._response, data), target="http")
        self.push(Stream(self._response, None), target="http")
        self.push(Kill())

    def _on_stdout_read(self, data):
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

class Root(Controller):

    def GET(self, *args, **kwargs):
        self.expires(60*60*24*30)
        return self.serve_file(os.path.abspath("static/index.html"))

    def POST(self, input=None):
        if not input:
            return ""

        self.response.headers["Content-Type"] = "text/plain"

        if input.strip() == "inspect":
            return inspect(self)

        self.response.stream = True

        sid = self.request.sid
        self += Command(self.request, self.response, input, channel=sid)

        return self.response

from circuits import Debugger

(Server(("0.0.0.0", 8000)) + Debugger(events=False)
        + Static("/js", docroot="static/js")
        + Static("/css", docroot="static/css")
        + Sessions()
        + Logger()
        + Root()
        ).run()
