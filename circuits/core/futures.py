# Module:   future
# Date:     6th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Futures

...
"""

from uuid import uuid4 as uuid
from functools import update_wrapper

from pools import Pool
from utils import findcmp
from workers import Task, Worker

def future():
    def decorate(f):
        def wrapper(self, event, *args, **kwargs):
            event.future = True
            pool = getattr(self, "_pool", None)
            if pool is None:
                pool = findcmp(self.root, Pool)
            if pool is not None:
                setattr(self, "_pool", pool)
                return self.push(Task(f, self, *args, **kwargs),
                        target=pool)
            else:
                return Worker(channel=str(uuid())).push(
                        Task(f, self, *args, **kwargs))
        wrapper.event = True
        return update_wrapper(wrapper, f)
    return decorate
