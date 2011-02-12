# Module:   test_workers
# Date:     7th October 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Workers Tests"""

from circuits import Task, Worker

def f():
    x = 0
    i = 0
    while i < 1000000:
        x += 1
        i += 1
    return x

def test():
    w = Worker()

    x = w.push(Task(f))

    while not x.result: pass

    assert x.result
    assert x.value == 1000000

    w.stop()
