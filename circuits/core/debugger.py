"""
Debugger component used to debug each event in a system by printing
each event to sys.stderr or to a Logger Component instance.
"""
import os
import sys
from signal import SIGINT, SIGTERM
from traceback import format_exc, format_exception_only

from .components import BaseComponent
from .handlers import handler, reprhandler


class Debugger(BaseComponent):

    """Create a new Debugger Component

    Creates a new Debugger Component that listens to all events in the system
    printing each event to sys.stderr or a Logger Component.

    :var IgnoreEvents: list of events (str) to ignore
    :var IgnoreChannels: list of channels (str) to ignore
    :var enabled: Enabled/Disabled flag

    :param log: Logger Component instance or None (*default*)
    """

    IgnoreEvents = ["generate_events"]
    IgnoreChannels = []

    def __init__(self, errors=True, events=True, file=None, logger=None,
                 prefix=None, trim=None, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        super(Debugger, self).__init__()

        self._errors = errors
        self._events = events

        if isinstance(file, str):
            self.file = open(os.path.abspath(os.path.expanduser(file)), "a")
        elif hasattr(file, "write"):
            self.file = file
        else:
            self.file = sys.stderr

        self.logger = logger
        self.prefix = prefix
        self.trim = trim

        self.IgnoreEvents.extend(kwargs.get("IgnoreEvents", []))
        self.IgnoreChannels.extend(kwargs.get("IgnoreChannels", []))

    @handler("signal", channel="*")
    def _on_signal(self, signo, stack):
        if signo in [SIGINT, SIGTERM]:
            raise SystemExit(0)

    @handler("exception", channel="*", priority=100.0)
    def _on_exception(self, error_type, value, traceback,
                      handler=None, fevent=None):

        if not self._errors:
            return

        s = []

        if handler is None:
            handler = ""
        else:
            handler = reprhandler(handler)

        msg = "ERROR {0:s} ({1:s}) ({2:s}): {3:s}\n".format(
            handler, repr(fevent), repr(error_type), repr(value)
        )

        s.append(msg)
        s.append('Traceback (most recent call last):\n')
        s.extend(traceback)
        s.extend(format_exception_only(error_type, value))
        s.append("\n")

        if self.logger is not None:
            self.logger.error("".join(s))
        else:
            try:
                self.file.write("".join(s))
                self.file.flush()
            except IOError:
                pass

    @handler(priority=101.0)
    def _on_event(self, event, *args, **kwargs):
        """Global Event Handler

        Event handler to listen to all events printing
        each event to self.file or a Logger Component instance
        by calling self.logger.debug
        """

        try:
            if not self._events:
                return

            channels = event.channels

            if event.name in self.IgnoreEvents:
                return

            if all(channel in self.IgnoreChannels for channel in channels):
                return

            s = repr(event)

            if self.prefix:
                if hasattr(self.prefix, '__call__'):
                    s = "%s: %s" % (self.prefix(), s)
                else:
                    s = "%s: %s" % (self.prefix, s)

            if self.trim:
                s = "%s ...>" % s[:self.trim]

            if self.logger is not None:
                self.logger.debug(s)
            else:
                self.file.write(s)
                self.file.write("\n")
                self.file.flush()
        except Exception as e:
            sys.stderr.write("ERROR (Debugger): {}".format(e))
            sys.stderr.write("{}".format(format_exc()))
