#!/usr/bin/python -i

from types import ListType, ListType

from circuits import handler, Event, Component, Manager

class Hello(Event):
    "Hello Event"

class Test(Event):
    "Test Event"

class Error(Event):
    "Error Event"

class Values(Event):
    "Values Event"

class App(Component):

    def hello(self):
        return "Hello World!"

    def test(self):
        return self.push(Hello())

    def error(self):
        raise Exception("Error!")

    @handler("values", priority=2.0)
    def _value1(self):
        return "foo"

    @handler("values", priority=1.0)
    def _value2(self):
        return "bar"

    @handler("values", priority=0.0)
    def _value3(self):
        return self.push(Hello())


m = Manager()
app = App()
app.register(m)

while m: m.flush()

def test_value():
    x = m.push(Hello())
    while m: m.flush()
    assert "Hello World!" in x
    assert x.value == "Hello World!"

def test_nested_value():
    x = m.push(Test())
    while m: m.flush()
    assert x.value == "Hello World!"
    assert str(x) == "Hello World!"

def test_error_value():
    x = m.push(Error())
    while m: m.flush()
    etype, evalue, etraceback = x
    assert etype is Exception
    assert str(evalue) == "Error!"
    assert type(etraceback) is ListType

def test_multiple_values():
    v = m.push(Values())
    while m: m.flush()
    assert type(v.value) is ListType
    x = list(v)
    assert "foo" in v
    assert x == ["foo", "bar", "Hello World!"]
    assert x[0] == "foo"
    assert x[1] == "bar"
    assert x[2] == "Hello World!"
