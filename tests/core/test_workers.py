# Module:   test_workers
# Date:     7th October 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Workers Tests"""

from time import sleep

from circuits import Thread, Process
from circuits.core import handler, Event

class Test(Event):
    """Test Event"""

class AppThread(Thread):

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

class AppProcess(Process):

    def run(self):
        sleep(1)

def test_compat():
    from circuits.core import workers

    if workers.HAS_MULTIPROCESSING:
        assert workers.Thread is not workers.Process
    else:
        assert workers.Thread is workers.Process

def test_thread():
    app = AppThread()
    app.start()

    app.push(Test())

    app.join()
    app.flush()

    assert app.count == 5
    assert app.flag
    assert app.done

def test_process():
    app = AppProcess()
    app.start()

    assert app.alive

    app.join()

    assert not app.alive
