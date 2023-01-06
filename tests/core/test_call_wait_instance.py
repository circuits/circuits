#!/usr/bin/env python
import pytest

from circuits import Component, Event, handler


class wait(Event):
    """wait Event"""

    success = True


class hello(Event):
    """hello Event"""

    success = True


class App(Component):

    @handler("wait")
    def _on_wait(self):
        e = hello()
        x = self.fire(e)
        yield self.wait(e)
        yield x.value

    def hello(self):
        return "Hello World!"


@pytest.fixture
def app(simple_manager):
    return App().register(simple_manager)


def test_wait_instance(simple_manager, app):
    x = simple_manager.fire(wait())
    assert simple_manager.run_until("wait_success")

    value = x.value
    assert value == "Hello World!"
