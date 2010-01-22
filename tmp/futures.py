#!/usr/bin/python -i

"""Futures Implementation for circuits

An expression of the form future <Expression> is defined by how it
responds to an Eval message with environment E and customer C as
follows:[3] The future expression responds to the Eval message by
sending the customer C a newly created actor F (the proxy for the
response of evaluating <Expression>) as a return value concurrently
with sending <Expression> an Eval message with environment E and
customer F. The default behavior of F is as follows:

 * When F receives a request R, then it checks to see if it has already received a response (that can either be a return value or a thrown exception) from evaluating <Expression> proceeding as follows:

 1) If it already has a response V, then

    * If V is a return value, then it is sent the request R.
    * If V is an exception, then it is thrown to the customer of the request R.

  2) If it does not already have a response, then R is stored in the
     queue of requests inside the F.

    * When F receives the response V from evaluating <Expression>,
      then V is stored in F and
    * If V is a return value, then all of the queued requests are sent V.
    * If V is an exception, then it is thrown to the customer of the each
      queued request.
"""

from time import sleep

from circuits import Component, Thread, Manager, Debugger
from circuits.core import handler, Event, BaseComponent

class Future(Thread):

    def __init__(self, f, *args, **kwargs):
        super(Future, self).__init__()
        self._f = f
        self._r = None
        self._args = args
        self._kwargs = kwargs
        self.start()

    @handler("eval")
    def doEVAL(self):
        pass

    def run(self):
        try:
            self._r = self._f(*self._args, **self._kwargs)
        except Exception, error:
            self._r = error
        finally:
            self.stop()

class Test(Component):

    def _foo(self):
        sleep(5)
        return "foo"

    def foo(self):
        return Future(self._foo)

    def bar(self):
        return self.send(Event(), "foo")

m = Manager() + Debugger()
m += Test()
m.start()

x = m.send(Event(), "foo")
