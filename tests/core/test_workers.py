# Module:   test_workers
# Date:     7th October 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Workers Tests"""

from circuits import Thread
from circuits.core import handler, Event

class Test(Event):
    """Test Event"""

class App(Thread):

   count = 0
   flag = False
   done = False

   @handler("test")
   def test(self):
      self.flag = True

   def run(self):
      while self.alive:
         self.count += 1
         if self.count == 5:
            self.stop()

      self.done = True

def test_threads():
    app = App()
    app.start()

    app.push(Test())

    while app.alive: pass
    app.flush()

    assert app.count == 5
    assert app.flag
    assert app.done
