# Module:   test_tools
# Date:     13th March 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Tools Test Suite

Test all functionality of the tools package.
"""

import py

from circuits import Component
from circuits.tools import kill, graph, inspect, findroot, reprhandler

class A(Component):

    def __tick__(self):
        pass

    def foo(self):
        print "A!"

class B(Component):

    def __tick__(self):
        pass

    def foo(self):
        print "B!"

class C(Component):

    def __tick__(self):
        pass

    def foo(self):
        print "C!"

class D(Component):

    def __tick__(self):
        pass

    def foo(self):
        print "D!"

class E(Component):

    def __tick__(self):
        pass

    def foo(self):
        print "E!"

class F(Component):

    def __tick__(self):
        pass

    def foo(self):
        print "F!"

GRAPH = """\
* <A/* (queued=5, channels=1, handlers=6) [S]>
 * <B/* (queued=0, channels=1, handlers=2) [S]>
  * <C/* (queued=0, channels=1, handlers=1) [S]>
 * <D/* (queued=0, channels=1, handlers=3) [S]>
  * <E/* (queued=0, channels=1, handlers=2) [S]>
   * <F/* (queued=0, channels=1, handlers=1) [S]>"""

INSPECT = """\
 Registered Components: 0

 Tick Functions: 1
  <bound method A.__tick__ of <A/* (queued=0, channels=1, handlers=1) [S]>>

 Channels and Event Handlers: 1
  *:foo; 1
   <listener on ('foo',) {target='*', priority=0.0}>
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

    assert a.manager == a
    assert b.manager == a
    assert c.manager == b
    assert not c.components

    assert b in a.components
    assert d in a.components

    assert d.manager == a
    assert e.manager == d
    assert f.manager == e

    assert f in e.components
    assert e in d.components
    assert not f.components

    assert kill(d) == None

    assert a.manager == a
    assert b.manager == a
    assert c.manager == b
    assert not c.components

    assert b in a.components
    assert not d in a.components
    assert not e in d.components
    assert not f in e.components

    assert d.manager == d
    assert e.manager == e
    assert f.manager == f

    assert not d.components
    assert not e.components
    assert not f.components

def test_graph(tmpdir):
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

    assert a.manager == a
    assert b.manager == a
    assert c.manager == b
    assert not c.components

    assert b in a.components
    assert d in a.components

    assert d.manager == a
    assert e.manager == d
    assert f.manager == e

    assert f in e.components
    assert e in d.components
    assert not f.components

    tmpdir.ensure("A")
    name = str(tmpdir.join("A"))
    assert graph(a, name=name) == GRAPH

def test_inspect():
    a = A()
    s = inspect(a)
    assert s == INSPECT

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
    s = reprhandler(a, a.foo)
    assert s == "<listener on ('foo',) {target='*', priority=0.0}>"

    f = lambda: None
    py.test.raises(KeyError, reprhandler, a, f)
