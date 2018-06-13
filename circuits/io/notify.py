"""File Notification Support

A Component wrapping the inotify API using the pyinotify library.
"""
try:
    from pyinotify import IN_UNMOUNT
    from pyinotify import WatchManager, Notifier, ALL_EVENTS
    from pyinotify import IN_ACCESS, IN_MODIFY, IN_ATTRIB, IN_CLOSE_WRITE
    from pyinotify import IN_CREATE, IN_DELETE, IN_DELETE_SELF, IN_MOVE_SELF
    from pyinotify import IN_CLOSE_NOWRITE, IN_OPEN, IN_MOVED_FROM, IN_MOVED_TO
except ImportError:
    raise ImportError("No pyinotify support available. Is pyinotify installed?")

from circuits.core import BaseComponent, handler
from circuits.core.pollers import BasePoller, Poller
from circuits.core.utils import findcmp

from .events import (
    accessed, closed, created, deleted, modified, moved, opened, ready,
    unmounted,
)

MASK = ALL_EVENTS

EVENT_MAP = {
    IN_MOVED_TO: moved,
    IN_MOVE_SELF: moved,
    IN_MOVED_FROM: moved,
    IN_CLOSE_WRITE: closed,
    IN_CLOSE_NOWRITE: closed,
    IN_OPEN: opened,
    IN_DELETE_SELF: deleted,
    IN_DELETE: deleted,
    IN_CREATE: created,
    IN_ACCESS: accessed,
    IN_MODIFY: modified,
    IN_ATTRIB: modified,
    IN_UNMOUNT: unmounted,
}


class Notify(BaseComponent):

    channel = "notify"

    def __init__(self, channel=channel):
        super(Notify, self).__init__(channel=channel)

        self._poller = None
        self._wm = WatchManager()
        self._notifier = Notifier(self._wm, self._on_process_events)

    def _on_process_events(self, event):
        dir = event.dir
        mask = event.mask
        path = event.path
        name = event.name
        pathname = event.pathname

        for k, v in EVENT_MAP.items():
            if mask & k:
                self.fire(v(name, path, pathname, dir))

    def add_path(self, path, mask=None, recursive=False, auto_add=True):
        mask = mask or MASK
        self._wm.add_watch(path, mask, rec=recursive, auto_add=auto_add)

    def remove_path(self, path, recursive=False):
        wd = self._wm.get_wd(path)
        if wd:
            self._wm.rm_watch(wd, rec=recursive)

    @handler("ready")
    def _on_ready(self, component):
        self._poller.addReader(self, self._notifier._fd)

    @handler("registered", channel="*")
    def _on_registered(self, component, manager):
        if self._poller is None:
            if isinstance(component, BasePoller):
                self._poller = component
                self.fire(ready(self))
            else:
                if component is not self:
                    return
                component = findcmp(self.root, BasePoller)
                if component is not None:
                    self._poller = component
                    self.fire(ready(self))
                else:
                    self._poller = Poller().register(self)
                    self.fire(ready(self))

    @handler("started", channel="*", priority=1)
    def _on_started(self, event, component):
        if self._poller is None:
            self._poller = Poller().register(self)
            self.fire(ready(self))
            event.stop()

    @handler("_read", priority=1)
    def __on_read(self, fd):
        self._notifier.read_events()
        self._notifier.process_events()
