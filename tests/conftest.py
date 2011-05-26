# Module:   conftest
# Date:     6th December 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""py.test config"""

from time import sleep

import collections

from circuits import handler
from circuits.core.manager import TIMEOUT


def wait_event(m, name, channel=None, timeout=3.0):
    if channel is None:
        channel = m

    flag = False

    @handler(name, channel=channel)
    def on_event(self, *args, **kwargs):
        global flag
        flag = True

    m.addHandler(on_event)

    try:
        for i in range(int(timeout / TIMEOUT)):
            if flag:
                return True
            sleep(TIMEOUT)
    finally:
        m.removeHandler(on_event)


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
        ("wait_event", wait_event),
        ("wait_for", wait_for),
    ))
