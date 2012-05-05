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

import select
from time import time
from errno import EBADF, EINTR
from select import error as SelectError
from socket import error as SocketError, create_connection, \
    socket as create_socket, AF_INET, SOCK_STREAM
from threading import Thread

from .events import Event
from .components import BaseComponent

TIMEOUT = 0.01  # 10ms timeout


class Read(Event):
    """Read Event"""

    name = "_read"


class Write(Event):
    """Write Event"""

    name = "_write"


class Error(Event):
    """Error Event"""

    name = "_error"


class Disconnect(Event):
    """Disconnect Event"""

    name = "_disconnect"


class BasePoller(BaseComponent):

    BLOCK = "block"

    channel = None
    
    def __init__(self, timeout=TIMEOUT, channel=channel):
        super(BasePoller, self).__init__(channel=channel)

        self.timeout = timeout

        self._read = []
        self._write = []
        self._targets = {}
        self._polling = False
        
        self._ctrl_in, self._ctrl_out = self._create_control_con()

    def _create_control_con(self):
        server = create_socket(AF_INET, SOCK_STREAM)
        server.bind(("localhost", 0))
        server.listen(1)
        res_list = []
        def accept():
            sock, _ = server.accept()
            sock.setblocking(False)
            res_list.append(sock)
        at = Thread(target=accept)
        at.start()
        clnt_sock = create_connection(server.getsockname())
        at.join()
        return (clnt_sock, res_list[0])

    def interrupt_poll(self):
        self._ctrl_in.send(b"\0")

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
        return self._targets.get(fd, self.parent)

    @property
    def polling(self):
        return getattr(self, "_polling", False)


class Select(BasePoller):
    """Select(...) -> new Select Poller Component

    Creates a new Select Poller Component that uses the select poller
    implementation. This poller is not recommended but is available for legacy
    reasons as most systems implement select-based polling for backwards
    compatibility.
    """

    channel = "select"

    def __init__(self, timeout=TIMEOUT, channel=channel):
        super(Select, self).__init__(timeout, channel=channel)

        self._ts = time()
        self._load = 0.0
        self._read.append(self._ctrl_out)

    def _preenDescriptors(self):
        for socks in (self._read[:], self._write[:]):
            for sock in socks:
                try:
                    select.select([sock], [sock], [sock], 0)
                except Exception:
                    self.discard(sock)

    def poll(self, timeout=None):
        try:
            if not any([self._read, self._write]):
                return
            self._polling = True
            if timeout == self.BLOCK:
                r, w, _ = select.select(self._read, self._write, [])
            else:
                r, w, _ = select.select(self._read, self._write, [], 
                                  self.timeout if timeout is None else timeout)
        except ValueError as e:
            # Possibly a file descriptor has gone negative?
            return self._preenDescriptors()
        except TypeError as e:
            # Something *totally* invalid (object w/o fileno, non-integral
            # result) was passed
            return self._preenDescriptors()
        except (SelectError, SocketError, IOError) as e:
            # select(2) encountered an error
            if e.args[0] in (0, 2):
                # windows does this if it got an empty list
                if (not self._read) and (not self._write):
                    return
                else:
                    raise
            elif e.args[0] == EINTR:
                return
            elif e.args[0] == EBADF:
                return self._preenDescriptors()
            else:
                # OK, I really don't know what's going on.  Blow up.
                raise
        finally:
            self._polling = False

        for sock in w:
            if self.isWriting(sock):
                self.fire(Write(sock), self.getTarget(sock))

        for sock in r:
            if sock == self._ctrl_out:
                try:
                    sock.recv(1)
                except:
                    pass
                continue
            if self.isReading(sock):
                self.fire(Read(sock), self.getTarget(sock))


class Poll(BasePoller):
    """Poll(...) -> new Poll Poller Component

    Creates a new Poll Poller Component that uses the poll poller
    implementation.
    """

    channel = "poll"

    def __init__(self, timeout=TIMEOUT, channel=channel):
        super(Poll, self).__init__(timeout, channel=channel)

        self._map = {}
        self._poller = select.poll()

        self._disconnected_flag = (select.POLLHUP
                | select.POLLERR
                | select.POLLNVAL
        )
        
        self._read.append(self._ctrl_out)
        self._updateRegistration(self._ctrl_out)

    def _updateRegistration(self, fd):
        fileno = fd.fileno()

        try:
            self._poller.unregister(fileno)
        except KeyError:
            pass

        mask = 0

        if fd in self._read:
            mask = mask | select.POLLIN
        if fd in self._write:
            mask = mask | select.POLLOUT

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

    def poll(self, timeout=None):
        try:
            self._polling = True
            if timeout == self.BLOCK:
                l = self._poller.poll()
            else:
                l = self._poller.poll(1000*(self.timeout if timeout is None 
                                            else timeout))
        except SelectError as e:
            if e.args[0] == EINTR:
                return
            else:
                raise
        finally:
            self._polling = False


        for fileno, event in l:
            self._process(fileno, event)

    def _process(self, fileno, event):
        if fileno not in self._map:
            return

        fd = self._map[fileno]

        if event & self._disconnected_flag and not (event & select.POLLIN):
            self.fire(Disconnect(fd), self.getTarget(fd))
            self._poller.unregister(fileno)
            super(Poll, self).discard(fd)
            del self._map[fileno]
        else:
            try:
                if event & select.POLLIN:
                    self.fire(Read(fd), self.getTarget(fd))
                if event & select.POLLOUT:
                    self.fire(Write(fd), self.getTarget(fd))
            except Exception as e:
                self.fire(Error(fd, e), self.getTarget(fd))
                self.fire(Disconnect(fd), self.getTarget(fd))
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
        self._poller = select.epoll()

        self._disconnected_flag = (select.EPOLLHUP | select.EPOLLERR)

        self._read.append(self._ctrl_out)
        self._updateRegistration(self._ctrl_out)

    def _updateRegistration(self, fd):
        try:
            fileno = fd.fileno()
            self._poller.unregister(fileno)
        except (SocketError, IOError) as e:
            if e.args[0] == EBADF:
                keys = [k for k, v in list(self._map.items()) if v == fd]
                for key in keys:
                    del self._map[key]

        mask = 0

        if fd in self._read:
            mask = mask | select.EPOLLIN
        if fd in self._write:
            mask = mask | select.EPOLLOUT

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

    def poll(self, timeout=None):
        try:
            self._polling = True
            if timeout == self.BLOCK:
                l = self._poller.poll()
            else:
                l = self._poller.poll(self.timeout if timeout is None
                                      else timeout)
        except IOError as e:
            if e.args[0] == EINTR:
                return
        except SelectError as e:
            if e.args[0] == EINTR:
                return
            else:
                raise
        finally:
            self._polling = False
            

        for fileno, event in l:
            self._process(fileno, event)

    def _process(self, fileno, event):
        if fileno not in self._map:
            return

        fd = self._map[fileno]

        if event & self._disconnected_flag and not (event & select.POLLIN):
            self.fire(Disconnect(fd), self.getTarget(fd))
            self._poller.unregister(fileno)
            super(EPoll, self).discard(fd)
            del self._map[fileno]
        else:
            try:
                if event & select.EPOLLIN:
                    self.fire(Read(fd), self.getTarget(fd))
                if event & select.EPOLLOUT:
                    self.fire(Write(fd), self.getTarget(fd))
            except Exception as e:
                self.fire(Error(fd, e), self.getTarget(fd))
                self.fire(Disconnect(fd), self.getTarget(fd))
                self._poller.unregister(fileno)
                super(EPoll, self).discard(fd)
                del self._map[fileno]


class KQueue(BasePoller):
    """KQueue(...) -> new KQueue Poller Component

    Creates a new KQueue Poller Component that uses the kqueue poller
    implementation.
    """

    channel = "kqueue"

    def __init__(self, timeout=0.00001, channel=channel):
        super(KQueue, self).__init__(timeout, channel=channel)
        self._map = {}
        self._poller = select.kqueue()

        self._read.append(self._ctrl_out)
        self._map[self._ctrl_out.fileno()] = self._ctrl_out
        self._poller.control([select.kevent(self._ctrl_out,
            select.KQ_FILTER_READ, select.KQ_EV_ADD)], 0)

    def addReader(self, source, sock):
        super(KQueue, self).addReader(source, sock)
        self._map[sock.fileno()] = sock
        self._poller.control([select.kevent(sock,
            select.KQ_FILTER_READ, select.KQ_EV_ADD)], 0)

    def addWriter(self, source, sock):
        super(KQueue, self).addWriter(source, sock)
        self._map[sock.fileno()] = sock
        self._poller.control([select.kevent(sock,
            select.KQ_FILTER_WRITE, select.KQ_EV_ADD)], 0)

    def removeReader(self, sock):
        super(KQueue, self).removeReader(sock)
        self._poller.control([select.kevent(sock,
            select.KQ_FILTER_READ, select.KQ_EV_DELETE)], 0)

    def removeWriter(self, sock):
        super(KQueue, self).removeWriter(sock)
        self._poller.control([select.kevent(sock,
            select.KQ_FILTER_WRITE, select.KQ_EV_DELETE)], 0)

    def discard(self, sock):
        super(KQueue, self).discard(sock)
        del self._map[sock.fileno()]
        self._poller.control([select.kevent(sock,
            select.KQ_FILTER_WRITE | select.KQ_FILTER_READ,
            select.KQ_EV_DELETE)], 0)

    def poll(self, timeout=None):
        try:
            self._polling = True
            if timeout == self.BLOCK:
                l = self._poller.control(None, 1000)
            else:
                l = self._poller.control(None, 1000, self.timeout if timeout
                                         is None else timeout)
        except SelectError as e:
            if e[0] == EINTR:
                return
            else:
                raise
        finally:
            self._polling = False

        for event in l:
            self._process(event)

    def _process(self, event):
        if event.ident not in self._map:
            # shouldn't happen ?
            # we unregister the socket since we don't care about it anymore
            self._poller.control(
                [select.kevent(event.ident, event.filter,
                    select.KQ_EV_DELETE)], 0)
            return

        sock = self._map[event.ident]

        if event.flags & select.KQ_EV_ERROR:
            self.fire(Error(sock, "error"), self.getTarget(sock))
        elif event.flags & select.KQ_EV_EOF:
            self.fire(Disconnect(sock), self.getTarget(sock))
        elif event.filter == select.KQ_FILTER_WRITE:
            self.fire(Write(sock), self.getTarget(sock))
        elif event.filter == select.KQ_FILTER_READ:
            self.fire(Read(sock), self.getTarget(sock))

Poller = Select

__all__ = ("BasePoller", "Poller", "Select", "Poll", "EPoll", "KQueue")
