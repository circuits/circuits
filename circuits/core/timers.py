"""Timer component to facilitate timed events."""

from datetime import datetime
from time import mktime, time

from circuits.core.handlers import handler

from .components import BaseComponent


class Timer(BaseComponent):

    """Timer Component

    A timer is a component that fires an event once after a certain
    delay or periodically at a regular interval.
    """

    def __init__(self, interval, event, *channels, **kwargs):
        """
        :param interval: the delay or interval to wait for until
                         the event is fired. If interval is specified as
                         datetime, the interval is recalculated as the
                         time span from now to the given datetime.
        :type interval:  ``datetime`` or number of seconds as a ``float``

        :param event:    the event to fire.
        :type event:     :class:`~.events.Event`

        :param persist:  An optional keyword argument which if ``True``
                         will cause the event to be fired repeatedly
                         once per configured interval until the timer
                         is unregistered.  If ``False``, the event fires
                         exactly once after the specified interval, and
                         the timer is unregistered. **Default:** ``False``
        :type persist:   ``bool``
        """

        super(Timer, self).__init__()

        self.expiry = None
        self.interval = None
        self.event = event
        self.channels = channels
        self.persist = kwargs.get("persist", False)

        self.reset(interval)

    @handler("generate_events")
    def _on_generate_events(self, event):
        if self.expiry is None:
            return

        now = time()

        if now >= self.expiry:
            if self.unregister_pending:
                return
            self.fire(self.event, *self.channels)

            if self.persist:
                self.reset()
            else:
                self.unregister()
            event.reduce_time_left(0)
        else:
            event.reduce_time_left(self.expiry - now)

    def reset(self, interval=None):
        """
        Reset the timer, i.e. clear the amount of time already waited
        for.
        """

        if interval is not None and isinstance(interval, datetime):
            self.interval = mktime(interval.timetuple()) - time()
        elif interval is not None:
            self.interval = interval

        self.expiry = time() + self.interval

    @property
    def expiry(self):
        return getattr(self, "_expiry", None)

    @expiry.setter
    def expiry(self, seconds):
        self._expiry = seconds
