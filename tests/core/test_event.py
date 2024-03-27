"""Event Tests."""

import pytest

from circuits import Component, Event


class test(Event):
    """test Event."""


class App(Component):
    def test(self) -> str:
        return 'Hello World!'


def test_repr() -> None:
    app = App()
    while len(app):
        app.flush()

    e = test()

    s = repr(e)
    assert s == '<test[] ( )>'

    app.fire(e)

    s = repr(e)
    assert s == '<test[*] ( )>'


def test_create() -> None:
    app = App()
    while len(app):
        app.flush()

    e = Event.create('test')

    s = repr(e)
    assert s == '<test[] ( )>'

    app.fire(e)

    s = repr(e)
    assert s == '<test[*] ( )>'


def test_getitem() -> None:
    app = App()
    while len(app):
        app.flush()

    e = test(1, 2, 3, foo='bar')

    assert e[0] == 1
    assert e['foo'] == 'bar'

    def f(e, k):
        return e[k]

    pytest.raises(TypeError, f, e, None)


def test_setitem() -> None:
    app = App()
    while len(app):
        app.flush()

    e = test(1, 2, 3, foo='bar')

    assert e[0] == 1
    assert e['foo'] == 'bar'

    e[0] = 0
    e['foo'] = 'Hello'

    def f(e, k, v) -> None:
        e[k] = v

    pytest.raises(TypeError, f, e, None, None)

    assert e[0] == 0
    assert e['foo'] == 'Hello'


def test_subclass_looses_properties() -> None:
    class hello(Event):
        success = True

    e = hello().child('success')
    assert e.success is False
