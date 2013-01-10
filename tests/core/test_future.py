#!/usr/bin/python -i

import pytest
#pytest.skip("XXX: Broken -- Worker/Pool changes")

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
        return self.fire(Hello())

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
        return self.fire(Hello())

    @handler("error")
    @future()
    def _on_error(self):
        raise Exception("Hello World!")


def reraise(e):
    raise e


def test_simple():
    app = App()
    app.start()

    e = Test()

    x = app.fire(e)
    pytest.wait_for(x, "result")
    assert x.value == "Hello World!"


def test_error():
    app = App()
    app.start()

    e = Error()

    x = app.fire(e)
    pytest.wait_for(x, "errors")
    assert x.errors

    etype, evalue, etraceback = x.value
    assert etype is Exception
    pytest.raises(Exception, lambda e: reraise(e), evalue)
    assert isinstance(etraceback, list)


def test_base_simple():
    app = BaseApp()
    app.start()

    e = Test()

    x = app.fire(e)
    pytest.wait_for(x, "result")
    assert x.value == "Hello World!"


def test_base_error():
    app = BaseApp()
    app.start()

    e = Error()
    x = app.fire(e)
    pytest.wait_for(x, "errors")

    assert x.errors
    etype, evalue, etraceback = x.value
    assert etype is Exception
    pytest.raises(Exception, lambda e: reraise(e), evalue)
    assert isinstance(etraceback, list)
