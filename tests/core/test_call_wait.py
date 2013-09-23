#!/usr/bin/env python

import pytest

from circuits import handler, Component, Event


class BaseEvent(Event):
    """BaseEvent Event"""

    success = True


class wait(BaseEvent):
    """wait Event"""


class call(BaseEvent):
    """call Event"""


class long_call(BaseEvent):
    """long_call Event"""


class long_wait(BaseEvent):
    """long_wait Event"""


class wait_return(BaseEvent):
    """wait_return Event"""


class hello(BaseEvent):
    """hello Event"""


class foo(BaseEvent):
    """foo Event"""


class get_x(BaseEvent):
    """get_x Event"""


class get_y(BaseEvent):
    """get_y Event"""


class eval(BaseEvent):
    """eval Event"""


class App(Component):

    @handler("wait")
    def _on_wait(self):
        x = self.fire(hello())
        yield self.wait("hello")
        yield x.value

    @handler("call")
    def _on_call(self):
        x = yield self.call(hello())
        yield x.value

    def hello(self):
        return "Hello World!"

    def long_wait(self):
        x = self.fire(foo())
        yield self.wait("foo")
        yield x.value

    def wait_return(self):
        self.fire(foo())
        yield (yield self.wait("foo"))

    def long_call(self):
        x = yield self.call(foo())
        yield x.value

    def foo(self):
        for i in range(1, 10):
            yield i

    def get_x(self):
        return 1

    def get_y(self):
        return 2

    def eval(self):
        x = yield self.call(get_x())
        y = yield self.call(get_y())
        yield x.value + y.value


@pytest.fixture(scope="module")
def app(request, manager, watcher):
    app = App().register(manager)
    assert watcher.wait("registered")

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    return app


def test_wait_simple(manager, watcher, app):
    x = manager.fire(wait())
    assert watcher.wait("wait_success")

    value = x.value
    assert value == "Hello World!"


def call_simple(manager, watcher, app):
    x = manager.fire(call())
    assert watcher.wait("call_success")

    value = x.value
    assert value == "Hello World!"


def test_long_call(manager, watcher, app):
    x = manager.fire(long_call())
    assert watcher.wait("long_call_success")

    value = x.value
    assert value == list(range(1, 10))


def test_long_wait(manager, watcher, app):
    x = manager.fire(long_wait())
    assert watcher.wait("long_wait_success")

    value = x.value
    assert value == list(range(1, 10))


def test_wait_return(manager, watcher, app):
    x = manager.fire(wait_return())
    assert watcher.wait("wait_return_success")

    value = x.value
    assert value == list(range(1, 10))


def test_eval(manager, watcher, app):
    x = manager.fire(eval())
    assert watcher.wait("eval_success")

    value = x.value
    assert value == 3
