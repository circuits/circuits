"""Tools Test Suite

Test all functionality of the tools package.
"""
import pytest

from circuits import Component, reprhandler
from circuits.tools import findroot, inspect, kill, tryimport

try:
    from threading import current_thread
except ImportError:
    from threading import currentThread as current_thread  # NOQA


class A(Component):

    def foo(self):
        print("A!")


class B(Component):

    def foo(self):
        print("B!")


class C(Component):

    def foo(self):
        print("C!")


class D(Component):

    def foo(self):
        print("D!")


class E(Component):

    def foo(self):
        print("E!")


class F(Component):

    def foo(self):
        print("F!")


def test_kill():
    a = A()
    b = B()
    c = C()
    d = D()
    e = E()
    f = F()

    a += b
    b += c

    e += f
    d += e
    a += d

    assert a.parent == a
    assert b.parent == a
    assert c.parent == b
    assert not c.components

    assert b in a.components
    assert d in a.components

    assert d.parent == a
    assert e.parent == d
    assert f.parent == e

    assert f in e.components
    assert e in d.components
    assert not f.components

    assert kill(d) is None
    while len(a):
        a.flush()

    assert a.parent == a
    assert b.parent == a
    assert c.parent == b
    assert not c.components

    assert b in a.components
    assert d not in a.components
    assert e not in d.components
    assert f not in e.components

    assert d.parent == d
    assert e.parent == e
    assert f.parent == f

    assert not d.components
    assert not e.components
    assert not f.components


def test_inspect():
    a = A()
    s = inspect(a)

    assert "Components: 0" in s
    assert "Event Handlers: 2" in s
    assert "foo; 1" in s
    assert "<handler[*][foo] (A.foo)>" in s
    assert "prepare_unregister_complete; 1" in s
    assert "<handler[<instance of A>][prepare_unregister_complete] (A._on_prepare_unregister_complete)>" in s


def test_findroot():
    a = A()
    b = B()
    c = C()

    a += b
    b += c

    root = findroot(a)
    assert root == a

    root = findroot(b)
    assert root == a

    root = findroot(c)
    assert root == a


def test_reprhandler():
    a = A()
    s = reprhandler(a.foo)
    assert s == "<handler[*][foo] (A.foo)>"

    pytest.raises(AttributeError, reprhandler, lambda: None)


def test_tryimport():
    import os
    m = tryimport("os")
    assert m is os


def test_tryimport_obj():
    from os import path
    m = tryimport("os", "path")
    assert m is path


def test_tryimport_fail():
    m = tryimport("asdf")
    assert m is None
