"""File I/O

This module implements a wrapper for basic File I/O.
"""
try:
    from os import O_NONBLOCK
except ImportError:
    # If it fails, that's fine. the fcntl import
    # will fail anyway.
    pass

from collections import deque
from errno import EINTR, EWOULDBLOCK
from os import read as fd_read, write as fd_write
from sys import getdefaultencoding

from circuits.core import Component, Event, handler
from circuits.core.pollers import BasePoller, Poller
from circuits.core.utils import findcmp
from circuits.six import PY3, binary_type, string_types
from circuits.tools import tryimport

from .events import close, closed, eof, error, opened, read, ready

fcntl = tryimport("fcntl")

TIMEOUT = 0.2
BUFSIZE = 4096


class _open(Event):

    """_open Event"""


class File(Component):

    channel = "file"

    def init(self, filename, mode="r", bufsize=BUFSIZE, encoding=None,
             channel=channel):
        self._mode = mode
        self._bufsize = bufsize
        self._filename = filename
        self._encoding = encoding or getdefaultencoding()

        self._fd = None
        self._poller = None
        self._buffer = deque()
        self._closeflag = False

    @property
    def closed(self):
        return getattr(self._fd, "closed", True) \
            if hasattr(self, "_fd") else True

    @property
    def filename(self):
        return getattr(self, "_filename", None)

    @property
    def mode(self):
        return getattr(self, "_mode", None)

    @handler("ready")
    def _on_ready(self, component):
        self.fire(_open(), self.channel)

    @handler("_open")
    def _on_open(self, filename=None, mode=None, bufsize=None):
        self._filename = filename or self._filename
        self._bufsize = bufsize or self._bufsize
        self._mode = mode or self._mode

        if isinstance(self._filename, string_types[0]):
            kwargs = {"encoding": self._encoding} if PY3 else {}
            self._fd = open(self.filename, self.mode, **kwargs)
        else:
            self._fd = self._filename
            self._mode = self._fd.mode
            self._filename = self._fd.name
            self._encoding = getattr(self._fd, "encoding", self._encoding)

        if fcntl is not None:
            # Set non-blocking file descriptor (non-portable)
            flag = fcntl.fcntl(self._fd, fcntl.F_GETFL)
            flag = flag | O_NONBLOCK
            fcntl.fcntl(self._fd, fcntl.F_SETFL, flag)

        if "r" in self.mode or "+" in self.mode:
            self._poller.addReader(self, self._fd)

        self.fire(opened(self.filename, self.mode))

    @handler("registered", "started", channel="*")
    def _on_registered_or_started(self, component, manager=None):
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

    @handler("stopped", channel="*")
    def _on_stopped(self, component):
        self.fire(close())

    @handler("prepare_unregister", channel="*")
    def _on_prepare_unregister(self, event, c):
        if event.in_subtree(self):
            self._close()

    def _close(self):
        if self.closed:
            return

        self._poller.discard(self._fd)

        self._buffer.clear()
        self._closeflag = False
        self._connected = False

        try:
            self._fd.close()
        except EnvironmentError:
            pass

        self.fire(closed())

    def close(self):
        if not self._buffer:
            self._close()
        elif not self._closeflag:
            self._closeflag = True

    def _read(self):
        try:
            data = fd_read(self._fd.fileno(), self._bufsize)
            if not isinstance(data, binary_type):
                data = data.encode(self._encoding)

            if data:
                self.fire(read(data)).notify = True
            else:
                self.fire(eof())
                if not any(m in self.mode for m in ("a", "+")):
                    self.close()
                else:
                    self._poller.discard(self._fd)
        except (OSError, IOError) as exc:
            if exc.args[0] in (EWOULDBLOCK, EINTR):
                return
            else:
                self.fire(error(exc))
                self._close()

    def seek(self, offset, whence=0):
        self._fd.seek(offset, whence)

    def _write(self, data):
        try:
            if not isinstance(data, binary_type):
                data = data.encode(self._encoding)

            nbytes = fd_write(self._fd.fileno(), data)

            if nbytes < len(data):
                self._buffer.appendleft(data[nbytes:])
        except (OSError, IOError) as e:
            if e.args[0] in (EWOULDBLOCK, EINTR):
                return
            else:
                self.fire(error(e))
                self._close()

    def write(self, data):
        if self._poller is not None and not self._poller.isWriting(self._fd):
            self._poller.addWriter(self, self._fd)
        self._buffer.append(data)

    @handler("_disconnect")
    def __on_disconnect(self, sock):
        self._close()

    @handler("_read")
    def __on_read(self, sock):
        self._read()

    @handler("_write")
    def __on_write(self, sock):
        if self._buffer:
            data = self._buffer.popleft()
            self._write(data)

        if not self._buffer:
            if self._closeflag:
                self._close()
            elif self._poller.isWriting(self._fd):
                self._poller.removeWriter(self._fd)
