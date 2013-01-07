# Module:   test_workers
# Date:     7th October 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Workers Tests"""

import pytest

from circuits import Task, Worker


@pytest.fixture(scope="module")
def worker(request):
    worker = Worker(process=True)

    def finalizer():
        worker.stop()

    request.addfinalizer(finalizer)

    if request.config.option.verbose:
        from circuits import Debugger
        Debugger().register(worker)

    waiter = pytest.WaitEvent(worker, "started")
    worker.start()
    assert waiter.wait()

    return worker


def f():
    x = 0
    i = 0
    while i < 1000000:
        x += 1
        i += 1
    return x


def test(worker):
    x = worker.fire(Task(f))

    def test(obj, attr):
        return isinstance(obj._value, list)

    assert pytest.wait_for(x, None, test)

    assert x.value == [1000000, 1000000]
