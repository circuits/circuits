#!/usr/bin/python -i

from circuits import handler, Event, Component, Manager


class Hello(Event):
    "Hello Event"


class Test(Event):
    "Test Event"


class Foo(Event):
    "Foo Event"


class Values(Event):
    "Values Event"


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


m = Manager()
app = App()
app.register(m)

while m:
    m.flush()


def test_value():
    x = m.fire(Hello())

    while m:
        m.flush()

    assert "Hello World!" in x
    assert x.value == "Hello World!"


def test_nested_value():
    x = m.fire(Test())

    while m:
        m.flush()

    assert x.value == "Hello World!"
    assert str(x) == "Hello World!"


def test_value_notify():
    x = m.fire(Hello())
    x.notify = True

    while m:
        m.flush()

    assert "Hello World!" in x
    assert x.value == "Hello World!"
    assert app.value is x

    app.value = None


def test_nested_value_notify():
    x = m.fire(Test())
    x.notify = True

    while m:
        m.flush()

    assert x.value == "Hello World!"
    assert str(x) == "Hello World!"
    assert app.value is x

    app.value = None


def test_error_value():
    x = m.fire(Foo())
    while m:
        m.flush()
    etype, evalue, etraceback = x
    assert etype is Exception
    assert str(evalue) == "ERROR"
    assert isinstance(etraceback, list)


def test_multiple_values():
    v = m.fire(Values())

    while m:
        m.flush()

    assert isinstance(v.value, list)
    x = list(v)
    assert "foo" in v
    assert x == ["foo", "bar", "Hello World!"]
    assert x[0] == "foo"
    assert x[1] == "bar"
    assert x[2] == "Hello World!"
