# Module:	test_timers
# Date:		7th October 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Timers Test Suite

Test all functionality of the wtimersorkers module.
"""

import unittest
from time import sleep

from circuits import Timer
from circuits import listener, Event, Component, Manager


class Test(Event):
	"""Test(Event) -> Test Event"""


class Foo(Component):

	flag = False

	@listener("timer")
	def onTIMER(self):
		self.flag = True


class EventTestCase(unittest.TestCase):

	def testTimer(self):
		"""Test Timer

		Test Timer
		"""

		x = Manager()
		a = Foo()
		t = Timer(0.01, Test(), "timer")

		x += a
		x += t

		sleep(0.02)
		t.poll()
		x.flush()

		self.assertTrue(a.flag)

		x -= a
		x -= t

	def testPersistentTimer(self):
		"""Test Persistent Timers

		Test Persistent Timers
		"""

		x = Manager()
		a = Foo()
		t = Timer(0.01, Test(), "timer", persist=True)

		x += a
		x += t

		for i in xrange(5):
			sleep(0.02)
			t.poll()
			x.flush()
			self.assertTrue(a.flag)
			a.flag = False

		x -= a
		x -= t



def suite():
	return unittest.makeSuite(EventTestCase, "test")


if __name__ == "__main__":
	unittest.main()
