# Module:   bridge
# Date:     5th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Debugger Test Suite"""

import unittest

from circuits import Bridge
from circuits.core import handler, Event, Component, Manager


def wait():
    for x in xrange(100000):
        pass


class Foo(Component):

    flag = False

    @handler("foo")
    def onFOO(self):
        self.flag = True

    @handler("dummy")
    def onDUMMY(self):
        pass

class Bar(Component):

    flag = False

    @handler("bar")
    def onBAR(self):
        self.flag = True

    @handler("dummy")
    def onDUMMY(self):
        pass


class EventTestCase(unittest.TestCase):

    def testBridge(self):
        """Test Bridge

        Test Bridge
        """

        m1 = Manager()
        b1 = Bridge(bind=8000, nodes=[("127.0.0.1", 8001)])
        b1.IgnoreChannels.extend(["dummy"])
        foo = Foo()
        m1 += b1
        m1 += foo
        m1.start()

        m2 = Manager()
        b2 = Bridge(bind=8001, nodes=[("127.0.0.1", 8000)])
        b2.IgnoreChannels.extend(["dummy"])
        bar = Bar()
        m2 += b2
        m2 += bar
        m2.start()

        m1.push(Event(), "bar")
        m1.push(Event(), "dummy")
        wait()

        self.assertFalse(foo.flag)
        self.assertTrue(bar.flag)

        m2.push(Event(), "foo")
        m2.push(Event(), "dummy")
        wait()

        self.assertTrue(foo.flag)
        self.assertTrue(bar.flag)

        m1.stop()
        m2.stop()

        bar.unregister()
        b2.unregister()

        foo.unregister()
        b1.unregister()


def suite():
    return unittest.makeSuite(EventTestCase, "test")


if __name__ == "__main__":
    unittest.main()
