#!/usr/bin/python -i

from time import sleep
from types import TracebackType

from circuits import future, Event, Component, Manager, Debugger

class Hello(Event):
    "Hello Event"

class Test(Event):
    "Test Event"

class Delay(Event):
    "Delay Event"

class Error(Event):
    "Error Event"

class App(Component):

    def hello(self):
        return "Hello World!"

    def test(self):
        return self.push(Hello())

    @future()
    def delay(self, n=1):
        sleep(n)
        return self.push(Hello())

    def error(self):
        raise Exception("Error!")

m = Manager()
app = App()
app.register(m)
m.start()

def test_value():
    x = m.push(Hello())
    m.flush()
    assert x.value == "Hello World!"

def test_nested_value():
    x = m.push(Test())
    m.flush(); m.flush()
    assert x.value == "Hello World!"

def test_future_value():
    x = m.push(Delay(2))
    sleep(3)
    m.flush()
    assert x.value == "Hello World!"

def test_error_value():
    x = m.push(Error())
    m.flush()
    etype, evalue, etraceback = x
    assert etype is Exception
    assert evalue.message == "Error!"
    assert type(etraceback) is TracebackType
