# Module:   debugger
# Date:     2nd April 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""
Debugger component used to debug each event in a system by printing
each event to sys.stderr or to a Logger Component instnace.
"""

import sys
from cStringIO import StringIO
from traceback import format_tb

from circuits import handler, Event, Component


class Debug(Event):
    """Debug Event

    :param msg: Message to display
    :type msg: str
    """


class Debugger(Component):
    """Create a new Debugger Component

    Creates a new Debugger Component that filters all events in teh system
    printing each event to sys.stderr or a Logger Component.

    :var IgnoreEvents: list of events (str) to ignore
    :var IgnoreChannels: list of channels (str) to ignore
    :var enabled: Enabled/Disabled flag

    :param log: Logger Component instnace or None (*default*)
    """

    IgnoreEvents = []
    IgnoreChannels = []

    def __init__(self, errors=True, events=True, file=None, logger=None):
        "initializes x; see x.__class__.__doc__ for signature"

        super(Debugger, self).__init__()

        self.errors = errors
        self.events = events
        self.logger = logger

        if file is None:
            self.file = sys.stderr
        else:
            self.file = file

    @handler("error", filter=True)
    def error(self, *args, **kwargs):
        if not self.errors:
            return

        s = StringIO()

        if len(args) == 3:
            type, value, traceback = args
            s.write("ERROR (%s): %s\n" % (type, value))
            s.write("%s\n" % "".join(format_tb(traceback)))
        else:
            s.write("Unknown Error\n")
            s.write("args:   %s\n" % repr(args))
            s.write("kwargs: %s\n" % repr(kwargs))

        s.seek(0)

        if self.logger is not None:
            for line in s:
                self.logger.error(line)
        else:
            self.file.write(s.read())
            self.file.flush()

        s.close()

    @handler(filter=True)
    def event(self, event, *args, **kwargs):
        """Global Event Handler

        Event handler to listen and filter all events printing each event
        to self.file or a Logger Component instnace by calling self.logger.debug
        """

        if not self.events:
            return

        channel = event.channel
        if True in [event.name == name for name in self.IgnoreEvents]:
            return
        elif channel in self.IgnoreChannels:
            return
        else:
            if self.logger is not None:
                self.logger.debug(repr(event))
            else:
                self.file.write("%s\n" % repr(event))
                self.file.flush()
