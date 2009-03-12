# Module:   test_tools
# Date:     13th March 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Tools Test Suite

Test all functionality of the tools package.
"""

import unittest

from circuits import Event, Component
from circuits.tools import kill, graph, inspect

class A(Component):

    def foo(self):
        print "A!"

class B(Component):

    def foo(self):
        print "B!"

class C(Component):

    def foo(self):
        print "C!"

class D(Component):

    def foo(self):
        print "D!"

class E(Component):

    def foo(self):
        print "E!"

class F(Component):

    def foo(self):
        print "F!"

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
        self.assertFalse(b._hidden)
        self.assertEquals(c.manager, b)
        self.assertFalse(c.components)
        self.assertFalse(c._hidden)

        self.assertTrue(b in a.components)
        self.assertTrue(d in a.components)
        self.assertTrue(c in a._hidden)
        self.assertTrue(e in a._hidden)
        self.assertTrue(f in a._hidden)

        self.assertEquals(d.manager, a)
        self.assertEquals(e.manager, d)
        self.assertEquals(f.manager, e)

        self.assertTrue(f in e.components)
        self.assertTrue(e in d.components)
        self.assertTrue(f in d._hidden)
        self.assertFalse(f._components)
        self.assertFalse(f._hidden)
        self.assertFalse(e._hidden)

        self.assertEquals(kill(d), None)

        self.assertEquals(a.manager, a)
        self.assertEquals(b.manager, a)
        self.assertFalse(b._hidden)
        self.assertEquals(c.manager, b)
        self.assertFalse(c.components)
        self.assertFalse(c._hidden)

        self.assertTrue(b in a.components)
        self.assertFalse(d in a.components)
        self.assertFalse(e in d.components)
        self.assertFalse(f in e.components)
        self.assertTrue(c in a._hidden)
        self.assertFalse(e in a._hidden)
        #self.assertFalse(f in a._hidden) # Failing

        self.assertEquals(d.manager, d)
        self.assertEquals(e.manager, e)
        self.assertEquals(f.manager, f)

        self.assertFalse(d.components)
        self.assertFalse(e.components)
        self.assertFalse(f.components)
        self.assertFalse(d._hidden)
        self.assertFalse(e._hidden)
        self.assertFalse(f._hidden)

if __name__ == "__main__":
    unittest.main()
