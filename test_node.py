# Module:   test_pools
# Date:     22nd February 2011
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Pools Tests"""

from circuits import Task, Pool


def f():
    x = 0
    i = 0
    while i < 1000000:
        x += 1
        i += 1
    return x


from circuits import Debugger
p = Pool() + Debugger()
p.start()
