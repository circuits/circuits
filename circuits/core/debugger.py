# Module:   debugger
# Date:     2nd April 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""
Debugger component used to debug each event in a system by printing
each event to sys.stderr or to a Logger Component instnace.
"""

import os
import sys
from cStringIO import StringIO

from handlers import handler
from components import BaseComponent
from circuits.tools import reprhandler

class Debugger(BaseComponent):
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

    def __init__(self, errors=True, events=True, file=None, logger=None,
            chop=False, **kwargs):
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
        self.chop = chop

        self.IgnoreEvents.extend(kwargs.get("IgnoreEvents", []))
        self.IgnoreChannels.extend(kwargs.get("IgnoreChannels", []))

    @handler("exception", priority=100.0)
    def _on_exception(self, type, value, traceback, handler=None):
        if not self.errors:
            return

        s = StringIO()

        if handler is None:
            handler = ""
        else:
            handler = reprhandler(self.root, handler)

        s.write("ERROR %s(%s): %s\n" % ("%s " % handler, type, value))
        s.write("%s\n" % "".join(traceback))

        s.seek(0)

        if self.logger is not None:
            self.logger.error(s.getvalue())
        else:
            self.file.write(s.read())
            self.file.flush()

        s.close()

    @handler(priority=100.0)
    def _on_event(self, event, *args, **kwargs):
        """Global Event Handler

        Event handler to listen and filter all events printing each event
        to self.file or a Logger Component instnace by calling self.logger.debug
        """

        if not self.events:
            return

        channel = event.channel

        if True in [event.name == x.__name__ for x in self.IgnoreEvents]:
            return
        elif channel in self.IgnoreChannels:
            return
        else:
            s = repr(event)
            if self.chop:
                s = "%s ...>" % s[:75]
            if self.logger is not None:
                self.logger.debug(s)
            else:
                self.file.write("%s\n" % s)
                self.file.flush()
