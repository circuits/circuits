#!/usr/bin/python -i

from types import TracebackType

from circuits import Event, Component, Manager

class Hello(Event):
    "Hello Event"

class Test(Event):
    "Test Event"

class Error(Event):
    "Error Event"

class App(Component):

    def hello(self):
        return "Hello World!"

    def test(self):
        return self.push(Hello())

    def error(self):
        raise Exception("Error!")

m = Manager()
app = App()
app.register(m)

while m: m.flush()

def test_value():
    x = m.push(Hello())
    while m: m.flush()
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
    assert type(etraceback) is TracebackType
