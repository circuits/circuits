#!/usr/bin/env python

import pytest

from circuits import Component, Event


class BaseEvent(Event):
    """BaseEvent Event"""

    success = True


class TestWait(BaseEvent):
    """TestWait Event"""


class TestCall(BaseEvent):
    """TestCall Event"""


class TestLongCall(BaseEvent):
    """TestLongCall Event"""


class TestLongWait(BaseEvent):
    """TestLongCall Event"""


class Hello(BaseEvent):
    """Hello Event"""


class Foo(BaseEvent):
    """Foo Event"""


class GetX(BaseEvent):
    """Get X Event"""


class GetY(BaseEvent):
    """Get Y Event"""


class TestEval(BaseEvent):
    """Test Eval Event"""


class App(Component):

    def test_wait(self):
        x = self.fire(Hello())
        yield self.wait("hello")
        yield x.value

    def test_call(self):
        x = yield self.call(Hello())
        yield x.value

    def hello(self):
        return "Hello World!"

    def test_long_wait(self):
        x = self.fire(Foo())
        yield self.wait("foo")
        yield x.value

    def test_long_call(self):
        x = yield self.call(Foo())
        yield x.value

    def foo(self):
        for i in range(1, 10):
            yield i

    def get_x(self):
        return 1

    def get_y(self):
        return 2

    def test_eval(self):
        x = yield self.call(GetX())
        y = yield self.call(GetY())
        yield x.value + y.value


@pytest.fixture(scope="module")
def app(request, manager, watcher):
    app = App().register(manager)
    assert watcher.wait("registered")

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    return app


def test_wait(manager, watcher, app):
    x = manager.fire(TestWait())
    assert watcher.wait("test_wait_success")

    value = x.value
    assert value == "Hello World!"


def test_call(manager, watcher, app):
    x = manager.fire(TestCall())
    assert watcher.wait("test_call_success")

    value = x.value
    assert value == "Hello World!"


def test_long_call(manager, watcher, app):
    x = manager.fire(TestLongCall())
    assert watcher.wait("test_long_call_success")

    value = x.value
    assert value == list(range(1, 10))


def test_long_wait(manager, watcher, app):
    x = manager.fire(TestLongWait())
    assert watcher.wait("test_long_wait_success")

    value = x.value
    assert value == list(range(1, 10))


def test_eval(manager, watcher, app):
    x = manager.fire(TestEval())
    assert watcher.wait("test_eval_success")

    value = x.value
    assert value == 3
