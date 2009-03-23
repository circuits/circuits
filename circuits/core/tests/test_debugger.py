# Module:   debugger
# Date:     5th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Debugger Test Suite"""

import sys
import unittest
from StringIO import StringIO

from circuits import Debugger
from circuits.core import handler, Event, Component, Manager


class Test(Event):
    "Test(Event) -> Test Event"

class Foo(Component):

    @handler("foo")
    def onFOO(self):
        pass

    @handler("bar")
    def onBAR(self):
        pass

class Logger(object):

    msg = None

    def debug(self, msg):
        self.msg = msg


class EventTestCase(unittest.TestCase):

    def setUp(self):
        sys.stderr = StringIO()

    def testDebugger(self):
        """Test Debugger

        Test Debugger
        """

        manager = Manager()
        debugger = Debugger()
        foo = Foo()

        manager += debugger
        manager += foo

        debugger.events = True
        e = Event()
        manager.send(e, "foo")
        sys.stderr.seek(0)
        s = sys.stderr.read().strip()
        self.assertEquals(s, str(e))

        sys.stderr.seek(0)
        sys.stderr.truncate()

        debugger.events = False
        e = Event()
        manager.send(e, "foo")
        sys.stderr.seek(0)
        s = sys.stderr.read().strip()
        self.assertEquals(s, "")

        sys.stderr.seek(0)
        sys.stderr.truncate()


    def testIgnoreEvents(self):
        """Test Debugger's IgnoreEvents

        Test Debugger's IgnoreEvents
        """

        manager = Manager()
        debugger = Debugger()
        foo = Foo()

        manager += debugger
        manager += foo

        debugger.IgnoreEvents.extend([Test])
        debugger.events = True

        e = Event()
        manager.send(e, "foo")
        sys.stderr.seek(0)
        s = sys.stderr.read().strip()
        self.assertEquals(s, str(e))

        sys.stderr.seek(0)
        sys.stderr.truncate()

        e = Test()
        manager.send(e, "foo")
        sys.stderr.seek(0)
        s = sys.stderr.read().strip()
        self.assertEquals(s, "")

        sys.stderr.seek(0)
        sys.stderr.truncate()
        foo.unregister()

    def testIgnoreChannels(self):
        """Test Debugger's IgnoreChannels

        Test Debugger's IgnoreChannels
        """

        manager = Manager()
        debugger = Debugger()
        foo = Foo()

        manager += debugger
        manager += foo

        debugger.IgnoreChannels.extend([("*", "bar")])
        debugger.events = True

        e = Event()
        manager.send(e, "foo")
        sys.stderr.seek(0)
        s = sys.stderr.read().strip()
        self.assertEquals(s, str(e))

        sys.stderr.seek(0)
        sys.stderr.truncate()

        e = Event()
        manager.send(e, "bar")
        sys.stderr.seek(0)
        s = sys.stderr.read().strip()
        self.assertEquals(s, "")

        sys.stderr.seek(0)
        sys.stderr.truncate()
        foo.unregister()

    def testLogger(self):
        """Test Debugger Logger

        Test Debugger using dummy Logger-like
        object (normally logging.Logger)
        """

        manager = Manager()
        logger = Logger()
        foo = Foo()

        debugger = Debugger(logger=logger)
        manager += debugger
        manager += foo

        e = Event()
        manager.push(e, "foo")
        manager.flush()
        manager.flush()
        self.assertEquals(logger.msg, repr(e))

        foo.unregister()


def suite():
    return unittest.makeSuite(EventTestCase, "test")


if __name__ == "__main__":
    unittest.main()
