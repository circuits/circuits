#!/usr/bin/env python
"""Bridge Example

A Bridge example that demonstrates bidirectional parent/child
communications and displays the no. of events per second and latency.
"""
from __future__ import print_function

import sys
from signal import SIGINT, SIGTERM
from time import time
from traceback import format_exc

from circuits import Component, Event, handler, ipc


def log(msg, *args, **kwargs):
    sys.stderr.write("{0:s}{1:s}".format(msg.format(*args), kwargs.get("n", "\n")))
    sys.stderr.flush()


def error(e):
    log("ERROR: {0:s}", e)
    log(format_exc())


def status(msg, *args):
    log("\r\x1b[K{0:s}", msg.format(*args), n="")


class ping(Event):
    """ping Event"""


class pong(Event):
    """pong Event"""


class Child(Component):

    def ping(self, ts):
        self.fire(ipc(pong(ts, time())))


class App(Component):

    def init(self):
        self.events = 0
        self.stime = time()

        Child().start(process=True, link=self)

    def ready(self, *args):
        self.fire(ipc(ping(time())))

    def pong(self, ts1, ts2):
        latency = (ts2 - ts1) * 1000.0
        status(
            "{0:d} event/s @ {1:0.2f}ms latency".format(
                int(self.events / (time() - self.stime)),
                latency
            )
        )
        self.fire(ipc(ping(time())))

    def signal(self, signo, stack):
        if signo in [SIGINT, SIGTERM]:
            raise SystemExit(0)

    @handler()
    def on_event(self, *args, **kwargs):
        self.events += 1


App().run()
