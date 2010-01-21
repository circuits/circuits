#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Web Example with Heavy Request Handlers

A question was posted to the circuits-users discussion group:
    http://groups.google.com.au/group/circuits-users/browse_thread/thread/f5ce1565d315faad

This example addresses this issue.

NB: This only works with the circuits-dev branch at:
    http://hg.softcircuit.com.au/projects/circuits-dev/
"""

from time import sleep

from circuits import Thread, Debugger
from circuits.web.events import Stream
from circuits.web import Server, Controller, Logger, Sessions

class Task(Thread):

    channel = "task"

    def __init__(self, request, response, channel=channel):
        super(Task, self).__init__(channel=channel)

        self._request = request
        self._response = response

        self.start()

    def run(self):
        request = self._request
        response = self._response

        sleep(5) # Do some heavy work - like sleeping!

        data = "Hello World!"
        self.push(Stream(self._response, data), target="http")
        self.push(Stream(self._response, None), target="http")

        self.stop()
        self.unregister()

class Root(Controller):

    def index(self):
        return "Hello World!"

    def test(self):
        self.response.stream = True
        sid = self.request.sid
        Task(self.request, self.response, channel=sid).register(self)
        return self.response

(Server(8000) + Debugger() + Sessions() + Logger() + Root()).run()
