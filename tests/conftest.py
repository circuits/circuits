# Module:   conftest
# Date:     6th December 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""py.test config"""

from time import sleep

import collections

from circuits import Component, handler, tick
from circuits.core.manager import TIMEOUT


class Flag(object):
    ticks = 0
    status = False


class WaitEvent(object):
    def __init__(self, manager, name, channel=None, timeout=30):
        if channel is None:
            channel = getattr(manager, "channel", None)

        self.timeout = timeout
        self.manager = manager

        flag = Flag()

        @handler(name, channel=channel, priority=-10e9)
        def on_event(self, *args, **kwargs):
            flag.status = True

        @tick
        def on_tick(self):
            flag.ticks += 1

        self.manager.addHandler(on_event)
        self.manager.addHandler(on_tick)
        self.flag = flag
        self.handler = on_event

    def wait(self):
        try:
            while self.flag.ticks < self.timeout:
                if self.flag.status:
                    return True
                sleep(TIMEOUT)
        finally:
            self.manager.removeHandler(self.handler)


def wait_for(obj, attr, value=True, timeout=30):
    from circuits.core.manager import TIMEOUT
    for i in range(timeout):
        if isinstance(value, collections.Callable):
            if value(obj, attr):
                return True
        elif getattr(obj, attr) == value:
            return True
        sleep(TIMEOUT)


def pytest_namespace():
    return dict((
        ("WaitEvent", WaitEvent),
        ("wait_for", wait_for),
    ))
