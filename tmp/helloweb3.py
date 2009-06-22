#!/usr/bin/env python

from circuits.io import File
from circuits.tools import kill
from circuits import Component, Debugger
from circuits.web import BaseServer, Response

class Task(Component):

    channel = "task"

    def __init__(self, filename, event, **kwargs):
        channel = kwargs.get("channel", Task.channel)

        super(Task, self).__init__(channel=channel)

        self._event = event

        self._file = File(filename, "r", channel=channel)
        self._file.register(self)

    def read(self, data):
        request, response = self._event
        response.body = data
        self.push(Response(response), target="http")
        kill(self)

class Root(Component):

    def request(self, event, request, response):
        Task("/dev/urandom", event).register(self)

(BaseServer(8000) + Debugger() + Root()).run()
