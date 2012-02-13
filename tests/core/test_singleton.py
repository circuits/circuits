#!/usr/bin/env python

import pytest

from circuits import Component, Manager
from circuits.core.components import SingletonError


class App(Component):

    singleton = True


class Base(Component):
    pass

Base.singleton = Base


class A(Base):
    pass


class B(Base):
    pass


def test():
    m = Manager()
    app = App()
    app.register(m)

    while m:
        m.flush()

    def f():
        App().register(m)

    pytest.raises(SingletonError, f)


def test_type():
    m = Manager()
    app = App()
    app.register(m)

    a = A()
    a.register(app)

    while m:
        m.flush()

    def f():
        B().register(app)

    pytest.raises(SingletonError, f)
