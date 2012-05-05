# Module:   timers
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>
from circuits.core.handlers import handler
from circuits.core.utils import findcmp
from copy import copy

"""Timers

Timers component to facilitate timed eventd.
"""

from time import time, mktime
from datetime import datetime

from .components import BaseComponent

class TimerSchedule(BaseComponent):
    
    singleton = True
    _timers = []
    
    def add_timer(self, timer):
        i = 0;
        while i < len(self._timers) and timer.expiry > self._timers[i].expiry:
            i += 1
        self._timers.insert(i, timer)
    
    def remove_timer(self, timer):
        self._timers.remove(timer)

    def check_timers(self):
        now = time()
        for timer in copy(self._timers):
            if timer.expiry <= now:
                timer.trigger()

    def next_expiry(self):
        if len(self._timers) == 0:
            return None
        return self._timers[0].expiry

class Timer(BaseComponent):
    """
    ...
    """

    _schedule = None

    def __init__(self, interval, event, *channels, **kwargs):
        super(Timer, self).__init__()

        if isinstance(interval, datetime):
            self.interval = mktime(interval.timetuple()) - time()
        else:
            self.interval = interval

        self.event = event
        self.channels = channels

        self.persist = kwargs.get("persist", False)

        self._eTime = time() + self.interval

    @handler("registered", channel="*")
    def _on_registered(self, component, manager):
        if self._schedule is None:
            if isinstance(component, TimerSchedule):
                self._schedule = component
            elif component == self:
                component = findcmp(self.root, TimerSchedule)
                if component is not None:
                    self._schedule = component
                else:
                    self._schedule = TimerSchedule().register(self)
            if self._schedule is not None:
                self._schedule.add_timer(self)

    @handler("prepare_unregister", channel="*")
    def _on_prepare_unregister(self, event, c):
        if event.in_subtree(self):
            if self._schedule is not None:
                self._schedule.remove_timer(self)

    def trigger(self):
        self.fire(self.event, *self.channels)

        if self.persist:
            self.reset()
        else:
            self.unregister()

    def reset(self):
        """T.reset() -> None

        Reset the timer.
        """
        if self._schedule is not None:
            self._schedule.remove_timer(self)
        self._eTime = time() + self.interval
        if self._schedule is not None:
            self._schedule.add_timer(self)

    @property
    def expiry(self):
        return getattr(self, "_eTime", None)
    