# Module:   notify
# Date:     2nd March 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""File Notification Support

A Component wrapping the inotify API using the pyinotify library.
"""

from time import sleep, time

try:
    from pyinotify import IN_UNMOUNT
    from pyinotify import WatchManager, Notifier, ALL_EVENTS
    from pyinotify import IN_ACCESS, IN_MODIFY, IN_ATTRIB, IN_CLOSE_WRITE
    from pyinotify import IN_CREATE, IN_DELETE, IN_DELETE_SELF, IN_MOVE_SELF
    from pyinotify import IN_CLOSE_NOWRITE, IN_OPEN, IN_MOVED_FROM, IN_MOVED_TO
except ImportError:
    raise Exception("No pyinotify support available. Is pyinotify installed?")

from circuits.core import Event, Component

MASK = ALL_EVENTS


class AddPath(Event):
    """Add path to watch"""
    channel = 'add_path'


class RemovePath(Event):
    """Remove path from watch"""
    channel = 'remove_path'


class Moved(Event):
    """Moved Event"""


class Opened(Event):
    """Opened Event"""


class Closed(Event):
    """Closed Event"""


class Created(Event):
    """Created Event"""


class Deleted(Event):
    """Deleted Event"""


class Accessed(Event):
    """Accessed Event"""


class Modified(Event):
    """Modified Event"""


class Unmounted(Event):
    """Unmounted Event"""


EVENT_MAP = {
        IN_MOVED_TO:        Moved,
        IN_MOVE_SELF:       Moved,
        IN_MOVED_FROM:      Moved,
        IN_CLOSE_WRITE:     Closed,
        IN_CLOSE_NOWRITE:   Closed,
        IN_OPEN:            Opened,
        IN_DELETE_SELF:     Deleted,
        IN_DELETE:          Deleted,
        IN_CREATE:          Created,
        IN_ACCESS:          Accessed,
        IN_MODIFY:          Modified,
        IN_ATTRIB:          Modified,
        IN_UNMOUNT:         Unmounted,
}


class Notify(Component):

    channel = "notify"

    def __init__(self, freq=1, timeout=1, channel=channel):
        super(Notify, self).__init__(channel=channel)

        self._freq = freq
        self._wm = WatchManager()
        self._notifier = Notifier(self._wm, self._process, timeout=timeout)

    def _sleep(self, rtime):
        # Only consider sleeping if _freq is > 0
        if self._freq > 0:
            ctime = time()
            s = self._freq - (ctime - rtime)
            if s > 0:
                sleep(s)

    def __tick__(self):
        self._notifier.process_events()
        rtime = time()
        if self._notifier.check_events():
            self._sleep(rtime)
            self._notifier.read_events()

    def _process(self, event):
        dir = event.dir
        mask = event.mask
        path = event.path
        name = event.name
        pathname = event.pathname

        for k, v in EVENT_MAP.items():
            if mask & k:
                self.fire(v(name, path, pathname, dir))

    def add_path(self, path, mask=None, recursive=False):
        mask = mask or MASK
        self._wm.add_watch(path, mask, rec=recursive)

    def remove_path(self, path, recursive=False):
        wd = self._wm.get_wd(path)
        if wd:
            self._wm.rm_watch(wd, rec=recursive)
