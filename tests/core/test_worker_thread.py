# Module:   test_workers
# Date:     7th October 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Workers Tests"""

import pytest

from circuits import task, Worker


@pytest.fixture(scope="module")
def worker(request):
    worker = Worker()

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


def add(a, b):
    return a + b


def test(worker):
    x = worker.fire(task(f))

    assert pytest.wait_for(x, "result")

    assert x.result
    assert x.value == 1000000


def test_args(worker):
    x = worker.fire(task(add, 1, 2))

    assert pytest.wait_for(x, "result")

    assert x.result
    assert x.value == 3
