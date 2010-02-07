# Module:   future
# Date:     6th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Futures

Future Value object and decorator wrapping a Thread (by default).
"""

from sys import exc_info
from threading import Thread
from functools import update_wrapper

from circuits.core import Value

class Future(Value):

    def __init__(self, f, args, kwargs):
        super(Future, self).__init__(None, self)

        self.f = f
        self.args = args
        self.kwargs = kwargs

        self._task = Thread(target=self._run)
        self._task.setDaemon(True)
        self._task.start()

    def __repr__(self):
        type = "T"
        name = self.__class__.__name__
        running = self._task is not None and self._task.isAlive()
        format = "<%s (%s) runnine=%r for %r (args=%r kwargs=%r)>"
        return format % (name, type, running, self.f, self.args, self.kwargs)

    def _run(self):
        try:
            self.value = self.f(*self.args, **self.kwargs)
        except:
            self.errors = True
            self.value = exc_info()

def future(**config):
    def decorate(f):
        def wrapper(*args, **kwargs):
            return Future(f, args, kwargs, **config)
        return update_wrapper(wrapper, f)
    return decorate
