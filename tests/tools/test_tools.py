# Module:   test_tools
# Date:     13th March 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Tools Test Suite

Test all functionality of the tools package.
"""

import os

try:
    from threading import current_thread
except ImportError:
    from threading import currentThread as current_thread

import py

import circuits.tools
from circuits import Component
from circuits.tools import kill, inspect, findroot, reprhandler

class A(Component):

    def __tick__(self):
        pass

    def foo(self):
        print("A!")

class B(Component):

    def __tick__(self):
        pass

    def foo(self):
        print("B!")

class C(Component):

    def __tick__(self):
        pass

    def foo(self):
        print("C!")

class D(Component):

    def __tick__(self):
        pass

    def foo(self):
        print("D!")

class E(Component):

    def __tick__(self):
        pass

    def foo(self):
        print("E!")

class F(Component):

    def __tick__(self):
        pass

    def foo(self):
        print("F!")

INSPECT = """\
 Components: 0

 Tick Functions: 1
  <bound method A.__tick__ of <A/* %s (queued=0) [S]>>

 Event Handlers: 3
  unregister; 1
   <listener[*.unregister] (A._on_unregister)>
  foo; 1
   <listener[*.foo] (A.foo)>
  prepare_unregister_complete; 1
   <listener[*.prepare_unregister_complete] (A._on_prepare_unregister_complete)>
"""

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

    assert kill(d) == None
    while a:
        a.flush()

    assert a.parent == a
    assert b.parent == a
    assert c.parent == b
    assert not c.components

    assert b in a.components
    assert not d in a.components
    assert not e in d.components
    assert not f in e.components

    assert d.parent == d
    assert e.parent == e
    assert f.parent == f

    assert not d.components
    assert not e.components
    assert not f.components

def test_inspect():
    a = A()
    s = inspect(a)
    id = "%s:%s" % (os.getpid(), current_thread().getName())

    assert s == INSPECT % id

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
    assert s == "<listener[*.foo] (A.foo)>"

    f = lambda: None
    py.test.raises(AttributeError, reprhandler, f)
