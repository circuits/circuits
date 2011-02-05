# Module:   future
# Date:     6th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Futures

Future Value object and decorator wrapping a Thread (by default).
"""

from uuid import uuid4 as uuid
from functools import update_wrapper

from utils import findcmp
from pools import NewTask, Task, Worker, ThreadPool

def future():
    def decorate(f):
        def wrapper(self, event, *args, **kwargs):
            event.future = True
            pool = findcmp(self.root, ThreadPool)
            if pool is not None:
                return self.push(NewTask(f, self, *args, **kwargs),
                        target=pool)
            else:
                return Worker(str(uuid())).push(
                        Task(f, self, *args, **kwargs))
        wrapper.event = True
        return update_wrapper(wrapper, f)
    return decorate
