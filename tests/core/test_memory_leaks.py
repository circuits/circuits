#!/usr/bin/env python
import pytest

from circuits import Component, Event, handler


class call(Event):

    """call Event"""
    success = True


class hello(Event):

    """hello Event"""
    success = True


class App(Component):
    @handler("call")
    def _on_call(self):
        x = yield self.call(hello())
        yield x.value

    def hello(self):
        return "Hello World!"


@pytest.fixture
def app(simple_manager):
    return App().register(simple_manager)


def test_done_handlers_dont_leak(simple_manager, app):
    simple_manager.fire(call())
    simple_manager.fire(call())
    assert simple_manager.run_until("call_success")
    assert "hello_done" not in app._handlers
