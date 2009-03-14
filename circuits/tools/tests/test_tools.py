# Module:   test_tools
# Date:     13th March 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Tools Test Suite

Test all functionality of the tools package.
"""

import unittest

from circuits import Component
from circuits.tools import kill, graph, inspect

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
* <A/* (q: 3 c: 1 h: 6) [S]>
 * <B/* (q: 0 c: 1 h: 2) [S]>
  * <C/* (q: 0 c: 1 h: 1) [S]>
 * <D/* (q: 1 c: 1 h: 3) [S]>
  * <E/* (q: 1 c: 1 h: 2) [S]>
   * <F/* (q: 0 c: 1 h: 1) [S]>"""

INSPECT = """\
 Registered Components: 2
  <D/* (q: 1 c: 1 h: 3) [S]>
  <B/* (q: 0 c: 1 h: 2) [S]>

 Tick Functions: 6
  <bound method F.__tick__ of <F/* (q: 0 c: 1 h: 1) [S]>>
  <bound method B.__tick__ of <B/* (q: 0 c: 1 h: 2) [S]>>
  <bound method C.__tick__ of <C/* (q: 0 c: 1 h: 1) [S]>>
  <bound method E.__tick__ of <E/* (q: 1 c: 1 h: 2) [S]>>
  <bound method D.__tick__ of <D/* (q: 1 c: 1 h: 3) [S]>>
  <bound method A.__tick__ of <A/* (q: 3 c: 1 h: 6) [S]>>

 Channels and Event Handlers: 1
  *:foo; 6
   <handler ('foo',) {filter: False, target: None) of <F/* (q: 0 c: 1 h: 1) [S]>>
   <handler ('foo',) {filter: False, target: None) of <D/* (q: 1 c: 1 h: 3) [S]>>
   <handler ('foo',) {filter: False, target: None) of <B/* (q: 0 c: 1 h: 2) [S]>>
   <handler ('foo',) {filter: False, target: None) of <A/* (q: 3 c: 1 h: 6) [S]>>
   <handler ('foo',) {filter: False, target: None) of <C/* (q: 0 c: 1 h: 1) [S]>>
   <handler ('foo',) {filter: False, target: None) of <E/* (q: 1 c: 1 h: 2) [S]>>
"""

class TestKill(unittest.TestCase):
    """Test kill() function

    Test the kill function and ensure that the entire structure of x
    is completely destroyed and they all becoems separate isolated
    components with no associations with any other component.
    """

    def runTest(self):
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

        self.assertEquals(a.manager, a)
        self.assertEquals(b.manager, a)
        self.assertEquals(c.manager, b)
        self.assertFalse(c.components)

        self.assertTrue(b in a.components)
        self.assertTrue(d in a.components)

        self.assertEquals(d.manager, a)
        self.assertEquals(e.manager, d)
        self.assertEquals(f.manager, e)

        self.assertTrue(f in e.components)
        self.assertTrue(e in d.components)
        self.assertFalse(f._components)

        self.assertEquals(kill(d), None)

        self.assertEquals(a.manager, a)
        self.assertEquals(b.manager, a)
        self.assertEquals(c.manager, b)
        self.assertFalse(c.components)

        self.assertTrue(b in a.components)
        self.assertFalse(d in a.components)
        self.assertFalse(e in d.components)
        self.assertFalse(f in e.components)

        self.assertEquals(d.manager, d)
        self.assertEquals(e.manager, e)
        self.assertEquals(f.manager, f)

        self.assertFalse(d.components)
        self.assertFalse(e.components)
        self.assertFalse(f.components)

class TestGraph(unittest.TestCase):
    """Test graph() function

    Test the graph function and ensure that the represented structure of x
    is correct.
    """

    def runTest(self):
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

        self.assertEquals(a.manager, a)
        self.assertEquals(b.manager, a)
        self.assertEquals(c.manager, b)
        self.assertFalse(c.components)

        self.assertTrue(b in a.components)
        self.assertTrue(d in a.components)

        self.assertEquals(d.manager, a)
        self.assertEquals(e.manager, d)
        self.assertEquals(f.manager, e)

        self.assertTrue(f in e.components)
        self.assertTrue(e in d.components)
        self.assertFalse(f._components)

        self.assertEquals(graph(a), GRAPH)

class TestInspect(unittest.TestCase):
    """Test inspect() function

    Test the inspect function and ensure that the represented structure of x
    and it's registered components and hidden components are correct.
    """

    def runTest(self):
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

        self.assertEquals(a.manager, a)
        self.assertEquals(b.manager, a)
        self.assertEquals(c.manager, b)
        self.assertFalse(c.components)

        self.assertTrue(b in a.components)
        self.assertTrue(d in a.components)

        self.assertEquals(d.manager, a)
        self.assertEquals(e.manager, d)
        self.assertEquals(f.manager, e)

        self.assertTrue(f in e.components)
        self.assertTrue(e in d.components)
        self.assertFalse(f._components)

        self.assertEquals(inspect(a), INSPECT)

if __name__ == "__main__":
    unittest.main()
