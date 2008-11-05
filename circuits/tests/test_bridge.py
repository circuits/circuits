# Module:	test_bridge
# Date:		5th November 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Debugger Test Suite

Test all functionality of the bridge module.
"""

import unittest

from circuits import Bridge
from circuits import listener, Event, Component, Manager

class Foo(Component):

	flag = False

	@listener("foo")
	def onFOO(self):
		self.flag = True

	@listener("dummy")
	def onDUMMY(self):
		pass

class Bar(Component):

	flag = False

	@listener("bar")
	def onBAR(self):
		self.flag = True

	@listener("dummy")
	def onDUMMY(self):
		pass


class EventTestCase(unittest.TestCase):

	def testBridge(self):
		"""Test Bridge

		Test Bridge
		"""

		m1 = Manager()
		b1 = Bridge(8000, nodes=[("127.0.0.1", 8001)])
		b1.IgnoreChannels.extend(["dummy"])
		foo = Foo()
		m1 += b1
		m1 += foo

		m2 = Manager()
		b2 = Bridge(8001, "127.0.0.1", nodes=[("127.0.0.1", 8000)])
		b2.IgnoreChannels.extend(["dummy"])
		bar = Bar()
		m2 += b2
		m2 += bar

		m1.push(Event(), "bar")
		m1.push(Event(), "dummy")
		for i in xrange(10):
			m1.flush()
			b1.poll()
			b2.poll()
			m2.flush()

		self.assertFalse(foo.flag)
		self.assertTrue(bar.flag)

		m2.push(Event(), "foo")
		m2.push(Event(), "dummy")
		for i in xrange(10):
			m2.flush()
			b2.poll()
			b1.poll()
			m1.flush()

		self.assertTrue(foo.flag)
		self.assertTrue(bar.flag)

		b2.close()
		for i in xrange(10):
			m2.flush()
			b2.poll()

		b1.close()
		for i in xrange(10):
			m1.flush()
			b1.poll()

		bar.unregister()
		b2.unregister()

		foo.unregister()
		b1.unregister()


def suite():
	return unittest.makeSuite(EventTestCase, "test")


if __name__ == "__main__":
	unittest.main()
