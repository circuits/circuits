# Module:   future
# Date:     6th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Futures

Future Value object and decorator wrapping a Thread (by default).
"""

from sys import exc_info
from threading import Thread
from traceback import format_tb
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
            self.value = self.f(self.manager, *self.args, **self.kwargs)
        except:
            etype, evalue, etraceback = exc_info()
            self.errors = True
            self.value = etype, evalue, format_tb(etraceback)

def future():
    def decorate(f):
        def wrapper(manager, *args, **kwargs):
            return Future(None, manager, f, args, kwargs)
        return update_wrapper(wrapper, f)
    return decorate
