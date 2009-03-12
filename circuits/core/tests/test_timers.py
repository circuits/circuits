# Module:   timers
# Date:     7th October 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Timers Test Suite"""

import unittest
from time import sleep

from circuits import Timer
from circuits.core import handler, Event, Component, Manager


class Test(Event):
    """Test(Event) -> Test Event"""


class Foo(Component):

    flag = False

    @handler("timer")
    def onTIMER(self):
        self.flag = True


class EventTestCase(unittest.TestCase):

    def testTimer(self):
        """Test Timer

        Test Timer
        """

        x = Manager()
        x.start()
        a = Foo()
        x += a
        x += Timer(0.01, Test(), "timer")

        sleep(0.1)

        self.assertTrue(a.flag)

        a.unregister()
        x.stop()


    def testPersistentTimer(self):
        """Test Persistent Timers

        Test Persistent Timers
        """

        x = Manager()
        x.start()
        a = Foo()
        x += a
        x += Timer(0.01, Test(), "timer", persist=True)

        for i in xrange(5):
            sleep(0.1)
            self.assertTrue(a.flag)
            a.flag = False

        a.unregister()
        x.stop()


def suite():
    return unittest.makeSuite(EventTestCase, "test")


if __name__ == "__main__":
    unittest.main()
