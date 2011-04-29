# Module:   conftest
# Date:     6th December 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""py.test config"""

from time import sleep

import collections


class Waiter(object):
    flag = False

    def handler(self, *args, **kwargs):
        self.flag = True


def wait_event(m, channel, target=None, timeout=3.0):
    from circuits.core.manager import TIMEOUT

    waiter = Waiter()

    if target is None:
        target = m

    m.addHandler(waiter.handler, channel, target=target)

    for i in range(int(timeout / TIMEOUT)):
        if waiter.flag:
            return True
        sleep(TIMEOUT)


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
