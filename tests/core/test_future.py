#!/usr/bin/python -i

from types import ListType

import pytest

from circuits import future, handler, BaseComponent, Component, Event

class Hello(Event):
    """Hello Event"""

class Test(Event):
    """Test Event"""

class Error(Event):
    """Error Event"""

class App(Component):

    def hello(self):
        return "Hello World!"

    @future()
    def test(self):
        return self.push(Hello())

    @future()
    def error(self):
        raise Exception("Hello World!")

class BaseApp(BaseComponent):

    @handler("hello")
    def _on_hello(self):
        return "Hello World!"

    @handler("test")
    @future()
    def _on_test(self):
        return self.push(Hello())

    @handler("error")
    @future()
    def _on_error(self):
        raise Exception("Hello World!")

def reraise(e):
    raise e

def test():
    app = App()
    while app: app.flush()
    e = Test()
    assert e.future == False
    x = app.push(e)
    while not x.result:
        app.flush()
    assert e.future == True
    assert x.value == "Hello World!"

def test_error():
    app = App()
    while app: app.flush()
    e = Error()
    assert e.future == False
    x = app.push(e)
    while not x.errors:
        app.flush()
    assert e.future == True
    assert x.errors
    etype, evalue, etraceback = x.value
    assert etype is Exception
    pytest.raises(Exception, lambda e: reraise(e), evalue)
    assert type(etraceback) is ListType

def test_base():
    app = BaseApp()
    while app: app.flush()
    e = Test()
    assert e.future == False
    x = app.push(e)
    while not x.result:
        app.flush()
    assert e.future == True
    assert x.value == "Hello World!"

def test_base_error():
    app = BaseApp()
    while app: app.flush()
    e = Error()
    assert e.future == False
    x = app.push(e)
    while not x.errors:
        app.flush()
    assert e.future == True
    assert x.errors
    etype, evalue, etraceback = x.value
    assert etype is Exception
    pytest.raises(Exception, lambda e: reraise(e), evalue)
    assert type(etraceback) is ListType
