# Module:   future
# Date:     6th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Futures

circuits supports the concept of "future" events. In circuits futures are
event handlers that are specially designed to be run in the background
either in a Thread or a Process. If you have event handlers that may
potentially "block" then wrapping them by the @future decorator unblocks
the bottle-neck caused by the "blocking" event handler(s).

Support for using a Thread or Process pool is also supported by specifying
an optional `pool` keyword argument and supplying an instance to a
``circuits.core.pool.Pool``.
"""

from uuid import uuid4 as uuid
from functools import update_wrapper

from .values import Value
from .utils import findcmp
from .workers import Worker
from .pools import Pool, Task


def future(pool=None):
    """Decorator to wrap an event handler in a future Task

    This decorator wraps an event handler into a background Task
    executing the event handler function in the background.

    :param pool: An optional thread/process pool
    :type pool: Pool
    """

    def decorate(f):
        def wrapper(self, event, *args, **kwargs):
            event.future = True
            p = getattr(self, "_pool", pool)
            if p is None:
                p = findcmp(self.root, Pool)
            if p is not None:
                setattr(self, "_pool", p)
                return self.push(Task(f, self, *args, **kwargs), target=p)
            else:
                return Worker(channel=str(uuid())).push(
                        Task(f, self, *args, **kwargs))
        wrapper.event = True
        return update_wrapper(wrapper, f)
    return decorate
