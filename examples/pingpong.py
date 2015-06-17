#!/usr/bin/env python


"""Bridge Example

A Bridge example that demonstrates bidirectional parent/child
communications and displays the no. of events per second and latency.
"""


from __future__ import print_function

import sys
from time import time
from traceback import format_exc
from signal import SIGINT, SIGTERM


from circuits import child, handler, Event, Component, Timer


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


class display(Event):
    """display Event"""


class Child(Component):

    def ping(self, ts):
        self.fire(child(pong(ts, time())))


class App(Component):

    def init(self):
        self.events = 0
        self.latency = 0
        self.stime = time()

        Child().start(process=True, link=self)
        Timer(0.5, display(), persist=True).register(self)

    def ready(self, *args):
        self.fire(child(ping(time())))

    def pong(self, ts1, ts2):
        self.latency = (ts2 - ts1) * 1000.0
        self.fire(child(ping(time())))

    def display(self):
        status(
            "{0:d} event/s @ {1:0.2f}ms latency".format(
                int(self.events / (time() - self.stime)),
                self.latency
            )
        )

    def signal(self, signo, stack):
        if signo in [SIGINT, SIGTERM]:
            raise SystemExit(0)

    @handler()
    def on_event(self, *args, **kwargs):
        self.events += 1


App().run()
