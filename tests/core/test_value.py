#!/usr/bin/python -i

import pytest

from circuits import handler, Event, Component


class Hello(Event):
    "Hello Event"


class Test(Event):
    "Test Event"


class Foo(Event):
    "Foo Event"


class Values(Event):
    "Values Event"

    complete = True


class App(Component):

    def hello(self):
        return "Hello World!"

    def test(self):
        return self.fire(Hello())

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
        return self.fire(Hello())


@pytest.fixture
def app(request, manager, watcher):
    app = App().register(manager)
    print
    print("[1] Waiting for App to be registered")
    watcher.wait("registered")
    print("[1] App registered")

    def finalizer():
        app.unregister()
        print
        print("[2] Waiting for App to be unregistered")
        watcher.wait("unregistered")
        print("[2] App unregistered")

    request.addfinalizer(finalizer)

    return app


def test_value(app, watcher):
    x = app.fire(Hello())
    watcher.wait("hello")

    assert "Hello World!" in x
    assert x.value == "Hello World!"


def test_nested_value(app, watcher):
    x = app.fire(Test())
    watcher.wait("test")

    assert x.value == "Hello World!"
    assert str(x) == "Hello World!"


def test_value_notify(app, watcher):
    x = app.fire(Hello())
    x.notify = True

    watcher.wait("hello_value_changed")

    assert "Hello World!" in x
    assert x.value == "Hello World!"
    assert app.value is x


def test_nested_value_notify(app, watcher):
    x = app.fire(Test())
    x.notify = True

    watcher.wait("hello_value_changed")

    assert x.value == "Hello World!"
    assert str(x) == "Hello World!"
    assert app.value is x


def test_error_value(app, watcher):
    x = app.fire(Foo())
    watcher.wait("foo")

    etype, evalue, etraceback = x
    assert etype is Exception
    assert str(evalue) == "ERROR"
    assert isinstance(etraceback, list)


def test_multiple_values(app, watcher):
    v = app.fire(Values())
    watcher.wait("values_complete")

    assert isinstance(v.value, list)

    x = list(v)

    assert "foo" in v
    assert x == ["foo", "bar", "Hello World!"]
    assert x[0] == "foo"
    assert x[1] == "bar"
    assert x[2] == "Hello World!"
