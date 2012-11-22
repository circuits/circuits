# Module:   debugger
# Date:     2nd April 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""
Debugger component used to debug each event in a system by printing
each event to sys.stderr or to a Logger Component instance.
"""

import os
import sys

from .handlers import handler
from .components import BaseComponent
from circuits.tools import reprhandler


class Debugger(BaseComponent):
    """Create a new Debugger Component

    Creates a new Debugger Component that filters all events in the system
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

        self.errors = errors
        self.events = events

        if type(file) is str:
            self.file = open(os.path.abspath(os.path.expanduser(file)), "a")
        elif type(file) is file or hasattr(file, "write"):
            self.file = file
        else:
            self.file = sys.stderr

        self.logger = logger
        self.prefix = prefix
        self.trim = trim

        self.IgnoreEvents.extend(kwargs.get("IgnoreEvents", []))
        self.IgnoreChannels.extend(kwargs.get("IgnoreChannels", []))

    @handler("error", channel="*", priority=100.0)
    def _on_error(self, error_type, value, traceback, handler=None):
        if not self.errors:
            return

        s = []

        if handler is None:
            handler = ""
        else:
            handler = reprhandler(handler)

        msg = "ERROR %s (%s): %s\n" % (handler, error_type, value)
        s.append(msg)
        s.extend(traceback)
        s.append("\n")

        if self.logger is not None:
            self.logger.error("".join(s))
        else:
            try:
                self.file.write("".join(s))
                self.file.flush()
            except IOError:
                pass

    @handler(channel="*", priority=101.0)
    def _on_event(self, event, *args, **kwargs):
        """Global Event Handler

        Event handler to listen and filter all events printing
        each event to self.file or a Logger Component instance
        by calling self.logger.debug
        """

        if not self.events:
            return

        channels = event.channels

        if event.name in self.IgnoreEvents:
            return

        if all(channel in self.IgnoreChannels for channel in channels):
            return

        s = repr(event)

        if self.prefix:
            s = "%s: %s" % (self.prefix, s)

        if self.trim:
            s = "%s ...>" % s[:self.trim]

        if self.logger is not None:
            self.logger.debug(s)
        else:
            try:
                self.file.write(s)
                self.file.write("\n")
                self.file.flush()
            except IOError:
                pass
