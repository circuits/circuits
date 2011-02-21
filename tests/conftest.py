# Module:   conftest
# Date:     6th December 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""py.test config"""

from time import sleep

from circuits.core.manager import TIMEOUT

def wait_for(obj, attr, value=True, timeout=30.0):
    for i in range(int(timeout / TIMEOUT)):
        if callable(value):
            if value(obj, attr):
                return True
        elif getattr(obj, attr) == value:
            return True
        sleep(TIMEOUT)
    return False

def pytest_namespace():
    return dict((
        ("wait_for", wait_for),
    ))
