#!/usr/bin/python -i


import pytest


from types import TracebackType


from circuits import handler, Event, Component


class hello(Event):

    "Hhllo Event"


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
def app(request, manager, watcher):
    app = App().register(manager)
    assert watcher.wait("registered")

    def finalizer():
        app.unregister()
        assert watcher.wait("unregistered")

    request.addfinalizer(finalizer)

    return app


def test_value(app, watcher):
    x = app.fire(hello())
    assert watcher.wait("hello")

    assert "Hello World!" in x
    assert x.value == "Hello World!"


def test_nested_value(app, watcher):
    x = app.fire(test())
    assert watcher.wait("test")

    assert x.value == "Hello World!"
    assert str(x) == "Hello World!"


def test_value_notify(app, watcher):
    x = app.fire(hello())
    x.notify = True

    assert watcher.wait("hello_value_changed")

    assert "Hello World!" in x
    assert x.value == "Hello World!"
    assert app.value is x


def test_nested_value_notify(app, watcher):
    x = app.fire(test())
    x.notify = True

    assert watcher.wait("test_value_changed")

    assert x.value == "Hello World!"
    assert str(x) == "Hello World!"
    assert app.value is x


def test_error_value(app, watcher):
    x = app.fire(foo())
    assert watcher.wait("foo")

    etype, evalue, etraceback = x
    assert etype is Exception
    assert str(evalue) == "ERROR"
    assert isinstance(etraceback, TracebackType)


def test_multiple_values(app, watcher):
    v = app.fire(values())
    assert watcher.wait("values_complete")

    assert isinstance(v.value, list)

    x = list(v)

    assert "foo" in v
    assert x == ["foo", "bar", "Hello World!"]
    assert x[0] == "foo"
    assert x[1] == "bar"
    assert x[2] == "Hello World!"
