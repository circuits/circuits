# Module:   events
# Date:     10th June 2011
# Author:   James Mills <prologic@shortcircuit.net.au>

"""I/O Events

This module implements commonly used I/O events used by other I/O modules.
"""

from circuits.core import Event


class EOF(Event):
    """EOF Event"""


class Seek(Event):
    """Seek Event"""


class Read(Event):
    """Read Event"""


class Close(Event):
    """Close Event"""


class Write(Event):
    """Write Event"""


class Error(Event):
    """Error Event"""


class Opened(Event):
    """Opened Event"""


class Closed(Event):
    """Closed Event"""
