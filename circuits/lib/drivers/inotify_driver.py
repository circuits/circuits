# Module:   inotify_driver
# Date:     2nd March 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""INotify Driver

A driver for the inotify system using the pyinotify library.
"""

from circuits.lib.drivers import DriverError

try:
    from pyinotify import IN_UNMOUNT, IN_ISDIR
    from pyinotify import WatchManager, Notifier, ALL_EVENTS
    from pyinotify import IN_ACCESS, IN_MODIFY, IN_ATTRIB, IN_CLOSE_WRITE
    from pyinotify import IN_CREATE, IN_DELETE, IN_DELETE_SELF, IN_MOVE_SELF
    from pyinotify import IN_CLOSE_NOWRITE, IN_OPEN, IN_MOVED_FROM, IN_MOVED_TO
except ImportError:
    raise DriverError("No pyinotify support available.")

from circuits.core import Event, Component

MASK = ALL_EVENTS

class Moved(Event): pass
class Opened(Event): pass
class Closed(Event): pass
class Created(Event): pass
class Deleted(Event): pass
class Accessed(Event): pass
class Modified(Event): pass
class Unmounted(Event): pass

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
        IN_UNMOUNT:         Unmounted}

class INotifyDriver(Component):

    def __init__(self, *args, **kwargs):
        super(INotifyDriver, self).__init__(*args, **kwargs)

        self._manager = WatchManager()
        self._notifier = Notifier(self._manager, self._process, timeout=0.1)

    def __tick__(self):
        if self._notifier.check_events():
            self._notifier.read_events()
            self._notifier.process_events()

    def _process(self, event):
        dir = event.dir
        mask = event.mask
        path = event.path
        name = event.name
        pathname = event.pathname

        for k, v in EVENT_MAP.iteritems():
            if mask & k:
                e = v(name, path, pathname, dir=dir)
                c = e.name.lower()
                self.push(e, c)

    def add(self, path, mask=None, recursive=False):
        mask = mask or MASK
        self._manager.add_watch(path, mask, rec=recursive)

    def remove(self, path, recursive=False):
        wd = self._manager.get_wd(path)
        if wd:
            self._manager.rm_watch(wd, rec=recursive)
