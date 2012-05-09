# Module:   timers
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
from circuits.core.handlers import handler

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

    @handler("generate_events")
    def _on_generate_events(self, event):
        now = time()
        if now >= self._eTime:
            self.fire(self.event, *self.channels)

            if self.persist:
                self.reset()
            else:
                self.unregister()
            event.reduce_time_left(0)
        else:
            event.reduce_time_left(self._eTime - now)

    def reset(self):
        """T.reset() -> None

        Reset the timer.
        """

        self._eTime = time() + self.interval

    @property
    def expiry(self):
        return getattr(self, "_eTime", None)
