#!/usr/bin/env python
import pytest

from circuits.core import Component, Event, TimeoutError, handler


class wait(Event):

    """wait Event"""
    success = True


class call(Event):

    """call Event"""
    success = True


class hello(Event):

    """hello Event"""
    success = True


class App(Component):

    @handler('wait')
    def _on_wait(self, timeout=-1):
        result = self.fire(hello())
        try:
            yield self.wait('hello', timeout=timeout)
        except TimeoutError as e:
            yield e
        else:
            yield result

    @handler('hello')
    def _on_hello(self):
        return 'hello'

    @handler('call')
    def _on_call(self, timeout=-1):
        result = None
        try:
            result = yield self.call(hello(), timeout=timeout)
        except TimeoutError as e:
            yield e
        else:
            yield result


@pytest.fixture
def app(request, manager, watcher):
    app = App().register(manager)
    assert watcher.wait("registered")

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    return app


def test_wait_success(manager, watcher, app):
    x = manager.fire(wait(10))
    assert watcher.wait('wait_success')

    value = x.value

    assert value == 'hello'


def test_wait_failure(manager, watcher, app):
    x = manager.fire(wait(0))
    assert watcher.wait('wait_success')

    value = x.value

    assert isinstance(value, TimeoutError)


def test_call_success(manager, watcher, app):
    x = manager.fire(call(10))
    assert watcher.wait('call_success')

    value = x.value

    assert value == 'hello'


def test_call_failure(manager, watcher, app):
    x = manager.fire(call(0))
    assert watcher.wait('call_success')

    value = x.value

    assert isinstance(value, TimeoutError)
