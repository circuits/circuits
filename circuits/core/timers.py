# Module:   timers
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Timers

Timers component to facilitate timed eventd.
"""

from time import time, mktime
from datetime import datetime

from components import Component

class Timer(Component):
    """Timer(s, e, c, t, persist) -> new timer component

    Creates a new timer object which when triggered
    will push the given event onto the event queue.

    s := no. of seconds to delay
    e := event to be fired
    c := channel to fire event to
    t := target to fire event to

    persist := Sets this timer as persistent if True.
    """

    def __init__(self, s, e, c="timer", t=None, persist=False):
        "initializes x; see x.__class__.__doc__ for signature"

        super(Timer, self).__init__()

        if isinstance(s, datetime):
            self.s = mktime(s.timetuple()) - time()
        else:
            self.s = s

        self.e = e
        self.c = c
        self.t = t
        self.persist = persist

        self.reset()

    def __tick__(self):
        self.poll()

    def reset(self):
        """T.reset() -> None

        Reset the timer.
        """

        self._eTime = time() + self.s

    def poll(self):
        """T.poll() -> state

        Check if this timer is ready to be triggered.
        If so, push the event onto the event queue.

        If timer is persistent, reset it after triggering.
        """

        if time() > self._eTime:
            self.push(self.e, self.c, self.t)

            if self.persist:
                self.reset()
                return False
            else:
                self.unregister()
                return True

        return None
