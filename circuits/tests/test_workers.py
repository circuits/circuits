# Module:   test_workers
# Date:     7th October 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Workers Test Suite

Test all functionality of the workers module.
"""

import unittest

from circuits.workers import Thread
from circuits.core import listener, Event, Manager

class Test(Event):
   """Test(Event) -> Test Event"""

class Foo(Thread):

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

   def testThread(self):
      """Test Thread

      Test Thread
      """

      x = Manager()
      w = Foo()
      x += w

      w.start()

      x.send(Test(), "foo")

      while w.isAlive():
          pass

      self.assertEquals(w.count, 5)
      self.assertTrue(w.done)

      x -= w


def suite():
   return unittest.makeSuite(EventTestCase, "test")

if __name__ == "__main__":
   unittest.main()
