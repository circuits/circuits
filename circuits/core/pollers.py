# Module:   pollers
# Date:     15th September 2008
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Poller Components for asynchronous file and socket I/O.

This module contains Poller components that enable polling of file or socket
descriptors for read/write events. Pollers:
   - Select
   - Poll
   - EPoll
"""

from errno import *
from time import time
from select import select
from select import error as SelectError
from socket import error as SocketError

try:
    from select import poll
    from select import POLLIN, POLLOUT, POLLHUP, POLLERR, POLLNVAL
    HAS_POLL = 1
except ImportError:
    HAS_POLL = 0

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

from events import Event
from components import BaseComponent

if HAS_POLL:
    _POLL_DISCONNECTED = (POLLHUP | POLLERR | POLLNVAL)

if HAS_EPOLL:
    _EPOLL_DISCONNECTED = (EPOLLHUP | EPOLLERR)

TIMEOUT = 0.2

###
### Events
###

class Read(Event): pass
class Write(Event): pass
class Error(Event): pass
class Disconnect(Event): pass

class BasePoller(BaseComponent):

    channel = None

    def __init__(self, timeout=TIMEOUT, channel=channel):
        super(BasePoller, self).__init__(channel=channel)

        self.timeout = timeout

        self._read = []
        self._write = []
        self._targets = {}

    def addReader(self, source, fd):
        channel = getattr(source, "channel", "*")
        self._read.append(fd)
        self._targets[fd] = channel

    def addWriter(self, source, fd):
        channel = getattr(source, "channel", "*")
        self._write.append(fd)
        self._targets[fd] = channel

    def removeReader(self, fd):
        if fd in self._read:
            self._read.remove(fd)
        if fd in self._targets:
            del self._targets[fd]

    def removeWriter(self, fd):
        if fd in self._write:
            self._write.remove(fd)
        if not (fd in self._read or fd in self._write):
            del self._targets[fd]

    def isReading(self, fd):
        return fd in self._read

    def isWriting(self, fd):
        return fd in self._write

    def discard(self, fd):
        if fd in self._read:
            self._read.remove(fd)
        if fd in self._write:
            self._write.remove(fd)
        if fd in self._targets:
            del self._targets[fd]

    def getTarget(self, fd):
        return self._targets.get(fd, self.manager)

class Select(BasePoller):
    """Select(...) -> new Select Poller Component

    Creates a new Select Poller Component that uses the select poller
    implementation. This poller is not reccomneded but is available for legacy
    reasons as most systems implement select-based polling for backwards
    compatibility.
    """

    channel = "select"

    def __init__(self, timeout=TIMEOUT, channel=channel):
        super(Select, self).__init__(timeout, channel=channel)

        self._ts = time()
        self._load = 0.0

    def _preenDescriptors(self):
        for socks in (self._read[:], self._write[:]):
            for sock in socks:
                try:
                    select([sock], [sock], [sock], 0)
                except Exception, e:
                    self.discard(sock)

    def __tick__(self):
        try:
            if not any([self._read, self._write]):
                return
            r, w, _ = select(self._read, self._write, [], self.timeout)
            if r or w:
                self.timeout = 0.0
            dtime = time() - self._ts
            self._ts = time()
            if not dtime == 0.0:
                load = float(len(r) + len(w)) / dtime
                if load > self._load:
                    if self.timeout > 0.1:
                        self.timeout -= 0.001
                else:
                    if self.timeout < 0.5:
                        self.timeout += 0.001
                self._load = load
        except ValueError, e:
            # Possibly a file descriptor has gone negative?
            return self._preenDescriptors()
        except TypeError, e:
            # Something *totally* invalid (object w/o fileno, non-integral
            # result) was passed
            return self._preenDescriptors()
        except (SelectError, SocketError, IOError), e:
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
            if self.isWriting(sock):
                self.push(Write(sock), "_write", self.getTarget(sock))
            
        for sock in r:
            if self.isReading(sock):
                self.push(Read(sock), "_read", self.getTarget(sock))

class Poll(BasePoller):
    """Poll(...) -> new Poll Poller Component

    Creates a new Poll Poller Component that uses the poll poller
    implementation.
    """

    channel = "poll"

    def __init__(self, timeout=TIMEOUT, channel=channel):
        super(Poll, self).__init__(timeout, channel=channel)

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

    def addReader(self, source, fd):
        super(Poll, self).addReader(source, fd)
        self._updateRegistration(fd)

    def addWriter(self, source, fd):
        super(Poll, self).addWriter(source, fd)
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

    def __tick__(self):
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
            self.push(Disconnect(fd), "_disconnect", self.getTarget(fd))
            self._poller.unregister(fileno)
            super(Poll, self).discard(fd)
            del self._map[fileno]
        else:
            try:
                if event & POLLIN:
                    self.push(Read(fd), "_read", self.getTarget(fd))
                if event & POLLOUT:
                    self.push(Write(fd), "_write", self.getTarget(fd))
            except Exception, e:
                self.push(Error(fd, e), "_error", self.getTarget(fd))
                self.push(Disconnect(fd), "_disconnect", self.getTarget(fd))
                self._poller.unregister(fileno)
                super(Poll, self).discard(fd)
                del self._map[fileno]

class EPoll(BasePoller):
    """EPoll(...) -> new EPoll Poller Component

    Creates a new EPoll Poller Component that uses the epoll poller
    implementation.
    """

    channel = "epoll"

    def __init__(self, timeout=TIMEOUT, channel=channel):
        super(EPoll, self).__init__(timeout, channel=channel)

        self._map = {}
        self._poller = epoll()

    def _updateRegistration(self, fd):
        try:
            fileno = fd.fileno()
            self._poller.unregister(fileno)
        except (SocketError, IOError), e:
            if e[0] == EBADF:
                keys = [k for k, v in self._map.items() if v == fd]
                for key in keys:
                    del self._map[key]

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

    def addReader(self, source, fd):
        super(EPoll, self).addReader(source, fd)
        self._updateRegistration(fd)

    def addWriter(self, source, fd):
        super(EPoll, self).addWriter(source, fd)
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

    def __tick__(self):
        try:
            l = self._poller.poll(self.timeout)
        except IOError, e:
            if e[0] == EINTR:
                return
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
            self.push(Disconnect(fd), "_disconnect", self.getTarget(fd))
            self._poller.unregister(fileno)
            super(EPoll, self).discard(fd)
            del self._map[fileno]
        else:
            try:
                if event & EPOLLIN:
                    self.push(Read(fd), "_read", self.getTarget(fd))
                if event & EPOLLOUT:
                    self.push(Write(fd), "_write", self.getTarget(fd))
            except Exception, e:
                self.push(Error(fd, e), "_error", self.getTarget(fd))
                self.push(Disconnect(fd), "_disconnect", self.getTarget(fd))
                self._poller.unregister(fileno)
                super(EPoll, self).discard(fd)
                del self._map[fileno]

### FIXME: The EPoll poller has some weird performance issues :/
#if HAS_EPOLL:
#    Poller = EPoll
#else:
#    Poller = Select

Poller = Select

__all__ = ("BasePoller", "Poller", "Select", "Poll", "EPoll",)
