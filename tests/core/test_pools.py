# Module:   test_pools
# Date:     22nd February 2011
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Pools Tests"""

import pytest

from circuits import Task, Pool

def f():
    x = 0
    i = 0
    while i < 1000000:
        x += 1
        i += 1
    return x

def test():
    p = Pool()
    p.start()

    x = p.push(Task(f))

    assert pytest.wait_for(x, "result")

    assert x.result
    v = x.value
    assert v == 1000000

    p.stop()
