# Module:   conftest
# Date:     6th December 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au
import os

"""py.test config"""

from time import sleep

import collections

from circuits import Component, handler
from circuits.core.manager import TIMEOUT


class Flag(object):
    status = False


def call_event_from_name(manager, event, event_name, *channels):
    fired = False
    value = None
    for r in manager.waitEvent(event_name):
        if not fired:
            fired = True
            value = manager.fire(event, *channels)
        sleep(0.1)
    return value


def call_event(manager, event, *channels):
    return call_event_from_name(manager, event, event.name, *channels)


class WaitEvent(object):
    def __init__(self, manager, name, channel=None, timeout=3.0):
        if channel is None:
            channel = getattr(manager, "channel", None)

        self.timeout = timeout
        self.manager = manager

        flag = Flag()

        @handler(name, channel=channel)
        def on_event(self, *args, **kwargs):
            flag.status = True

        self.manager.addHandler(on_event)
        self.flag = flag
        self.handler = on_event

    def wait(self):
        try:
            for i in range(int(self.timeout / TIMEOUT)):
                if self.flag.status:
                    return True
                sleep(TIMEOUT)
        finally:
            self.manager.removeHandler(self.handler)


def wait_for(obj, attr, value=True, timeout=3.0):
    from circuits.core.manager import TIMEOUT
    for i in range(int(timeout / TIMEOUT)):
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
        ("call_event", call_event),
        ("call_event_from_name", call_event_from_name),
    ))
