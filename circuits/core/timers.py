# Module:   timers
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
"""
Timer component to facilitate timed events.
"""

from circuits.core.handlers import handler

from time import time, mktime
from datetime import datetime

from .components import BaseComponent


class Timer(BaseComponent):
    """
    A timer is a component that fires an event once after a certain
    delay or periodically at a regular interval.
    """

    def __init__(self, interval, event, *channels, **kwargs):
        """
        :param interval: the delay or interval to wait for until
            the event is fired. If interval is specified as
            datetime, the interval is recalculated as the time span from
            now to the given datetime.
        :type interval: datetime or float number
        
        :param event: the event to fire.
        :type event: :class:`~.events.Event`
        
        If the optional keyword argument *persist* is set to ``True``,
        the event will be fired repeatedly. Else the timer fires the
        event once and then unregisters itself.
        """
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
            if self.unregister_pending:
                return
            self.fire(self.event, *self.channels)

            if self.persist:
                self.reset()
            else:
                self.unregister()
            event.reduce_time_left(0)
        else:
            event.reduce_time_left(self._eTime - now)

    def reset(self):
        """
        Reset the timer, i.e. clear the amount of time already waited
        for. 
        """

        self._eTime = time() + self.interval

    @property
    def expiry(self):
        return getattr(self, "_eTime", None)
