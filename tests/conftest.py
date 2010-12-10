# Module:   conftest
# Date:     6th December 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""py.test config"""

from time import time

def wait_for_flag(obj, attr, value=True, timeout=30.0):
    etime = time() + timeout
    while time() < etime:
        if getattr(obj, attr) == value:
            return True
    return False

def pytest_namespace():
    return dict((
        ("wait_for_flag", wait_for_flag),
    ))
