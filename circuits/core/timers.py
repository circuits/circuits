# Module:   timers
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Timers

Timers component to facilitate timed eventd.
"""

from time import time, mktime
from datetime import datetime

from .components import BaseComponent

class Timer(BaseComponent):
    """
    ...
    """

    def __init__(self, interval, event, *channels, **kwargs):
        super(Timer, self).__init__()

        if isinstance(interval, datetime):
            self.interval = mktime(interval.timetuple()) - time()
        else:
            self.interval = interval

        self.event = event
        self.channels = channels

        self.persist = kwargs.get("persist", False)

        self.reset()

    def __tick__(self):
        if time() > self._eTime:
            self.fire(self.event, *self.channels)

            if self.persist:
                self.reset()
            else:
                self.unregister()

    def reset(self):
        """T.reset() -> None

        Reset the timer.
        """

        self._eTime = time() + self.interval
