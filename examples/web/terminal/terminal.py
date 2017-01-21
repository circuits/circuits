#!/usr/bin/env python
import os
import signal
from StringIO import StringIO
from subprocess import PIPE, Popen

from circuits import Component, Debugger, Event, handler
from circuits.io import File
from circuits.net.events import write
from circuits.tools import inspect
from circuits.web import Controller, Logger, Server, Sessions, Static
from circuits.web.events import stream

BUFFERING = 1
STREAMING = 2


class kill(Event):

    """kill Event"""


class input(Event):

    """input Event"""


class Command(Component):

    channel = "cmd"

    def __init__(self, request, response, command, channel=channel):
        super(Command, self).__init__(channel=channel)

        self._request = request
        self._response = response
        self._command = command

        self._state = BUFFERING
        self._buffer = None

        self._p = Popen(
            command, shell=True, stdout=PIPE, stderr=PIPE,
            close_fds=True, preexec_fn=os.setsid
        )

        self._stdin = None
        if self._p.stdin is not None:
            self._stdin = File(self._p.stdin, channel="%s.stdin" % channel)
            self._stdin.register(self)

        self._stdout = File(self._p.stdout, channel="%s.stdout" % channel)
        self.addHandler(
            handler("eof", channel="%s.stdout" % channel)(self._on_stdout_eof)
        )
        self.addHandler(
            handler("read", channel="%s.stdout" % channel)(
                self._on_stdout_read
            )
        )
        self._stdout.register(self)

    @handler("disconnect", channel="web")
    def disconnect(self, sock):
        if sock == self._request.sock:
            self.fire(kill(), self)

    @handler("response", channel="web", priority=-1)
    def response(self, response):
        if response == self._response:
            self._state = STREAMING

    def kill(self):
        os.killpg(self._p.pid, signal.SIGINT)
        self.unregister()

    def input(self, data):
        if self._stdin is not None:
            self.fire(write(data), self._stdin)

    @staticmethod
    def _on_stdout_eof(self):
        if self._buffer is not None:
            self._buffer.flush()
            data = self._buffer.getvalue()
            self.fire(stream(self._response, data), "web")
        self.fire(stream(self._response, None), "web")
        self.fire(kill())

    @staticmethod
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
                self.fire(stream(self._response, data), "web")
            else:
                self.fire(stream(self._response, data), "web")


class Root(Controller):

    def GET(self, *args, **kwargs):
        self.expires(60 * 60 * 24 * 30)
        return self.serve_file(os.path.abspath("static/index.xhtml"))

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


app = Server(("0.0.0.0", 8000))
Debugger().register(app)
Static("/js", docroot="static/js").register(app)
Static("/css", docroot="static/css").register(app)
Sessions().register(app)
Logger().register(app)
Root().register(app)
app.run()
