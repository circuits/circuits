# Module:	test_workers
# Date:		7th October 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Workers Test Suite

Test all functionality of the workers module.
"""

import unittest

import circuits
from circuits import *
from circuits.workers import workers, Worker

class Test(Event):
	"""Test(Event) -> Test Event"""

class Foo(Worker):

	count = 0
	flag = False
	done = False

	@listener("foo")
	def onFOO(self):
		self.flag = True

	def run(self):
		while self.running:
			self.count += 1
			if self.count == 5:
				self.stop()

		self.done = True


class EventTestCase(unittest.TestCase):

	def testWorker(self):
		"""Test Worker

		Test Worker
		"""

		x = Manager()
		w = Foo()
		x += w

		w.start()

		x.send(Test(), "foo")

		for worker in workers():
			worker.join()

		self.assertEquals(w.count, 5)
		self.assertTrue(w.done)

		x -= w


def suite():
	return unittest.makeSuite(EventTestCase, "test")

if __name__ == "__main__":
	unittest.main()
