#!/usr/bin/env python
import pytest

from circuits import Component, Event, handler


class wait(Event):
    """wait Event"""
    success = True


class call(Event):
    """call Event"""
    success = True


class long_call(Event):
    """long_call Event"""
    success = True


class long_wait(Event):
    """long_wait Event"""
    success = True


class wait_return(Event):
    """wait_return Event"""
    success = True


class hello(Event):
    """hello Event"""
    success = True


class foo(Event):
    """foo Event"""
    success = True


class get_x(Event):
    """get_x Event"""
    success = True


class get_y(Event):
    """get_y Event"""
    success = True


class eval(Event):
    """eval Event"""
    success = True


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


@pytest.fixture
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


@pytest.mark.xfail(reason='Issue #226')
@pytest.mark.timeout(1)
def test_wait_too_late(manager, watcher, app):
    event = foo()
    manager.fire(event)
    assert watcher.wait("foo_success")
    manager.tick()

    x = manager.wait(event, timeout=.1)
    value = next(x)
    assert value == list(range(1, 10))
