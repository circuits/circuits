# Module:   future
# Date:     6th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Futures

Future Value object and decorator wrapping a Thread (by default).
"""

from sys import exc_info
from threading import Thread
from functools import update_wrapper

from values import Value

class Future(Value):

    def __init__(self, event, manager, f, args, kwargs):
        super(Future, self).__init__(event, manager)

        self.f = f
        self.args = args
        self.kwargs = kwargs

        self._task = Thread(target=self._run)
        self._task.setDaemon(True)
        self._task.start()

    def _run(self):
        try:
            self.value = self.f(self.event, *self.args, **self.kwargs)
        except:
            self.errors = True
            self.value = exc_info()

def future():
    def decorate(f):
        f._passEvent = True
        def wrapper(self, event, *args, **kwargs):
            return Future(event, self, f, args, kwargs)
        return update_wrapper(wrapper, f)
    return decorate
