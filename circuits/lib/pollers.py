# Module:   pollers
# Date:     15th September 2008
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Poller Components for asynchronous file and socket I/O.

This module contains Poller components that enable polling of file or socket
descriptors for read/write events. Pollers:
   - Select
   - Poll
   - EPoll
   - KQueue
"""

import warnings
from errno import *
from select import select, poll
from select import error as SelectError
from select import POLLIN, POLLOUT, POLLHUP, POLLERR, POLLNVAL

try:
    from select import epoll
    from select import EPOLLIN, EPOLLOUT, EPOLLHUP, EPOLLERR
    HAS_EPOLL = 2
except ImportError:
    try:
        from select26 import epoll
        from select26 import EPOLLIN, EPOLLOUT, EPOLLHUP, EPOLLERR
        HAS_EPOLL = 1
    except ImportError:
        HAS_EPOLL = 0
        warnings.warn("No epoll support available! But that's ok :)")

from circuits.core import handler, Event, BaseComponent

_POLL_DISCONNECTED = (POLLHUP | POLLERR | POLLNVAL)

if HAS_EPOLL:
    _EPOLL_DISCONNECTED = (EPOLLHUP | EPOLLERR)

TIMEOUT = 0.001

###
### Events
###

class Read(Event): pass
class Write(Event): pass
class Error(Event): pass
class Disconnect(Event): pass

class _Poller(BaseComponent):

    channel = "poll"

    def __init__(self, target, timeout=TIMEOUT, channel=channel):
        super(_Poller, self).__init__(channel=channel)

        self.target = target
        self.timeout = timeout

        self._read = []
        self._write = []

    def addReader(self, fd):
        self._read.append(fd)

    def addWriter(self, fd):
        self._write.append(fd)

    def removeReader(self, fd):
        self._read.remove(fd)

    def removeWriter(self, fd):
        self._write.remove(fd)

    def isReading(self, fd):
        return fd in self._read

    def isWriting(self, fd):
        return fd in self._write

    def discard(self, fd):
        if fd in self._read:
            self._read.remove(fd)
        if fd in self._write:
            self._write.remove(fd)

    def __tick__(self):
        self.poll()

    def poll(self):
        raise NotImplemented

class Select(_Poller):
    """Select(...) -> new Select Poller Component

    Creates a new Select Poller Component that uses the select poller
    implementation. This poller is not reccomneded but is available for legacy
    reasons as most systems implement select-based polling for backwards
    compatibility.
    """

    def _preenDescriptors(self):
        for socks in (self._read[:], self._write[:]):
            for sock in socks:
                try:
                    select([sock], [sock], [sock], 0)
                except Exception, e:
                    self.discard(sock)

    def poll(self):
        try:
            r, w, _ = select(self._read, self._write, [], self.timeout)
        except ValueError, e:
            # Possibly a file descriptor has gone negative?
            return self._preenDescriptors()
        except TypeError, e:
            # Something *totally* invalid (object w/o fileno, non-integral
            # result) was passed
            return self._preenDescriptors()
        except (SelectError, IOError), e:
            # select(2) encountered an error
            if e[0] in (0, 2):
                # windows does this if it got an empty list
                if (not self._read) and (not self._write):
                    return
                else:
                    raise
            elif e[0] == EINTR:
                return
            elif e[0] == EBADF:
                return self._preenDescriptors()
            else:
                # OK, I really don't know what's going on.  Blow up.
                raise

        for sock in w:
            self.send(Write(sock), "_write", self.target)
            
        for sock in r:
            self.send(Read(sock), "_read", self.target)

class Poll(_Poller):
    """Poll(...) -> new Poll Poller Component

    Creates a new Poll Poller Component that uses the poll poller
    implementation.
    """

    def __init__(self, *args, **kwargs):
        super(Poll, self).__init__(*args, **kwargs)

        self._map = {}
        self._poller = poll()

    def _updateRegistration(self, fd):
        fileno = fd.fileno()

        try:
            self._poller.unregister(fileno)
        except KeyError:
            pass

        mask = 0

        if fd in self._read:
            mask = mask | POLLIN
        if fd in self._write:
            mask = mask | POLLOUT

        if mask:
            self._poller.register(fd, mask)
            self._map[fileno] = fd
        else:
            super(Poll, self).discard(fd)
            del self._map[fileno]

    def addReader(self, fd):
        super(Poll, self).addReader(fd)
        self._updateRegistration(fd)

    def addWriter(self, fd):
        super(Poll, self).addWriter(fd)
        self._updateRegistration(fd)

    def removeReader(self, fd):
        super(Poll, self).removeReader(fd)
        self._updateRegistration(fd)

    def removeWriter(self, fd):
        super(Poll, self).removeWriter(fd)
        self._updateRegistration(fd)

    def discard(self, fd):
        super(Poll, self).discard(fd)
        self._updateRegistration(fd)

    def poll(self):
        try:
            l = self._poller.poll(self.timeout)
        except SelectError, e:
            if e[0] == EINTR:
                return
            else:
                raise

        for fileno, event in l:
            self._process(fileno, event)

    def _process(self, fileno, event):
        if fileno not in self._map:
            return

        fd = self._map[fileno]

        if event & _POLL_DISCONNECTED and not (event & POLLIN):
            self.send(Disconnect(fd), "_disconnect", self.target)
            self._poller.unregister(fileno)
            super(Poll, self).discard(fd)
            del self._map[fileno]
        else:
            try:
                if event & POLLIN:
                    self.send(Read(fd), "_read", self.target)
                if event & POLLOUT:
                    self.send(Write(fd), "_write", self.target)
            except Exception, e:
                self.send(Error(fd, e), "_error", self.target)
                self.send(Disconnect(fd), "_disconnect", self.target)
                self._poller.unregister(fileno)
                super(Poll, self).discard(fd)
                del self._map[fileno]

class EPoll(_Poller):
    """EPoll(...) -> new EPoll Poller Component

    Creates a new EPoll Poller Component that uses the epoll poller
    implementation.
    """

    def __init__(self, *args, **kwargs):
        super(EPoll, self).__init__(*args, **kwargs)

        self._map = {}
        self._poller = epoll()

    @handler("started", target="*")
    def started(self, component, mode):
        if mode in ("P", "T"):
            self._poller = epoll()

    def _updateRegistration(self, fd):
        fileno = fd.fileno()

        try:
            self._poller.unregister(fileno)
        except IOError:
            pass

        mask = 0

        if fd in self._read:
            mask = mask | EPOLLIN
        if fd in self._write:
            mask = mask | EPOLLOUT

        if mask:
            self._poller.register(fd, mask)
            self._map[fileno] = fd
        else:
            super(EPoll, self).discard(fd)

    def addReader(self, fd):
        super(EPoll, self).addReader(fd)
        self._updateRegistration(fd)

    def addWriter(self, fd):
        super(EPoll, self).addWriter(fd)
        self._updateRegistration(fd)

    def removeReader(self, fd):
        super(EPoll, self).removeReader(fd)
        self._updateRegistration(fd)

    def removeWriter(self, fd):
        super(EPoll, self).removeWriter(fd)
        self._updateRegistration(fd)

    def discard(self, fd):
        super(EPoll, self).discard(fd)
        self._updateRegistration(fd)

    def poll(self):
        try:
            l = self._poller.poll(self.timeout)
        except SelectError, e:
            if e[0] == EINTR:
                return
            else:
                raise

        for fileno, event in l:
            self._process(fileno, event)

    def _process(self, fileno, event):
        if fileno not in self._map:
            return

        fd = self._map[fileno]

        if event & _EPOLL_DISCONNECTED and not (event & POLLIN):
            self.send(Disconnect(fd), "_disconnect", self.target)
            self._poller.unregister(fileno)
            super(EPoll, self).discard(fd)
            del self._map[fileno]
        else:
            try:
                if event & EPOLLIN:
                    self.send(Read(fd), "_read", self.target)
                if event & EPOLLOUT:
                    self.send(Write(fd), "_write", self.target)
            except Exception, e:
                self.send(Error(fd, e), "_error", self.target)
                self.send(Disconnect(fd), "_disconnect", self.target)
                self._poller.unregister(fileno)
                super(EPoll, self).discard(fd)
                del self._map[fileno]

if not HAS_EPOLL:
    del EPoll
