"""I/O Events

This module implements commonly used I/O events used by other I/O modules.
"""
from circuits.core import Event


class eof(Event):

    """eof Event"""


class seek(Event):

    """seek Event"""


class read(Event):

    """read Event"""


class close(Event):

    """close Event"""


class write(Event):

    """write Event"""


class error(Event):

    """error Event"""


class open(Event):

    """open Event"""


class opened(Event):

    """opened Event"""


class closed(Event):

    """closed Event"""


class ready(Event):

    """ready Event"""


class started(Event):

    """started Event"""


class stopped(Event):

    """stopped Event"""


class moved(Event):

    """moved Event"""


class created(Event):

    """created Event"""


class deleted(Event):

    """deleted Event"""


class accessed(Event):

    """accessed Event"""


class modified(Event):

    """modified Event"""


class unmounted(Event):

    """unmounted Event"""
