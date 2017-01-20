"""Workers Tests"""

from os import getpid

import pytest

from circuits import Worker, task


@pytest.fixture
def worker(request, manager):
    worker = Worker().register(manager)

    def finalizer():
        worker.unregister()

    request.addfinalizer(finalizer)

    return worker


def err():
    return x * 2  # NOQA


def foo():
    x = 0
    i = 0
    while i < 1000000:
        x += 1
        i += 1
    return x


def pid():
    return "Hello from {0:d}".format(getpid())


def add(a, b):
    return a + b


def test_failure(manager, watcher, worker):
    e = task(err)
    e.failure = True

    x = worker.fire(e)

    assert watcher.wait("task_failure")

    assert isinstance(x.value[1], Exception)


def test_success(manager, watcher, worker):
    e = task(foo)
    e.success = True

    x = worker.fire(e)

    assert watcher.wait("task_success")

    assert x.value == 1000000


def test_args(manager, watcher, worker):
    e = task(add, 1, 2)
    e.success = True

    x = worker.fire(e)

    assert watcher.wait("task_success")

    assert x.value == 3
