"""Workers Tests"""


import pytest

from circuits import Worker, task

task.complete = True


@pytest.fixture
def worker(request, manager, watcher):
    worker = Worker().register(manager)
    assert watcher.wait("registered")

    def finalizer():
        worker.unregister()
        assert watcher.wait("unregistered")

    request.addfinalizer(finalizer)

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


def test(manager, watcher, worker):
    x = manager.fire(task(f))
    assert watcher.wait("task_complete")

    assert x.result
    assert x.value == 1000000


def test_args(manager, watcher, worker):
    x = manager.fire(task(add, 1, 2))
    assert watcher.wait("task_complete")

    assert x.result
    assert x.value == 3
