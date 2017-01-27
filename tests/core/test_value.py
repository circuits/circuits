#!/usr/bin/python -i
from types import TracebackType

import pytest

from circuits import Component, Event, handler


class hello(Event):

    "Hello Event"


class test(Event):

    "test Event"


class foo(Event):

    "foo Event"


class values(Event):

    "values Event"

    complete = True


class App(Component):

    def hello(self):
        return "Hello World!"

    def test(self):
        return self.fire(hello())

    def foo(self):
        raise Exception("ERROR")

    @handler("hello_value_changed")
    def _on_hello_value_changed(self, value):
        self.value = value

    @handler("test_value_changed")
    def _on_test_value_changed(self, value):
        self.value = value

    @handler("values", priority=2.0)
    def _value1(self):
        return "foo"

    @handler("values", priority=1.0)
    def _value2(self):
        return "bar"

    @handler("values", priority=0.0)
    def _value3(self):
        return self.fire(hello())


@pytest.fixture
def app(request, simple_manager):
    return App().register(simple_manager)


def test_value(app, simple_manager):
    x = app.fire(hello())
    simple_manager.run()

    assert "Hello World!" in x
    assert x.value == "Hello World!"


def test_nested_value(app, simple_manager):
    x = app.fire(test())
    simple_manager.run()

    assert x.value == "Hello World!"
    assert str(x) == "Hello World!"


def test_value_notify(app, simple_manager):
    ev = hello()
    ev.notify = True
    x = app.fire(ev)

    simple_manager.run()

    assert "Hello World!" in x
    assert x.value == "Hello World!"
    assert app.value is x


def test_nested_value_notify(app, simple_manager):
    ev = test()
    ev.notify = True
    x = app.fire(ev)

    simple_manager.run()

    assert x.value == "Hello World!"
    assert str(x) == "Hello World!"
    assert app.value is x


def test_error_value(app, simple_manager):
    x = app.fire(foo())
    simple_manager.run()

    etype, evalue, etraceback = x
    assert etype is Exception
    assert str(evalue) == "ERROR"
    assert isinstance(etraceback, TracebackType)


def test_multiple_values(app, simple_manager):
    v = app.fire(values())
    simple_manager.run()

    assert isinstance(v.value, list)

    x = list(v)

    assert "foo" in v
    assert x == ["foo", "bar", "Hello World!"]
    assert x[0] == "foo"
    assert x[1] == "bar"
    assert x[2] == "Hello World!"
