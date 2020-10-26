"""Poller Components for asynchronous file and socket I/O.

This module contains Poller components that enable polling of file or socket
descriptors for read/write events. Pollers:
- Select
- Poll
- EPoll
"""
import os
import platform
import select
from errno import EBADF, EINTR
from select import error as SelectError
from socket import (
    AF_INET, SOCK_STREAM, create_connection, error as SocketError, socket,
)
from threading import Thread

from circuits.core.handlers import handler

from .components import BaseComponent
from .events import Event


class _read(Event):

    """_read Event"""


class _write(Event):

    """_write Event"""


class _error(Event):

    """_error Event"""


class _disconnect(Event):

    """_disconnect Event"""


class BasePoller(BaseComponent):

    channel = None

    def __init__(self, channel=channel):
        super(BasePoller, self).__init__(channel=channel)

        self._read = []
        self._write = []
        self._targets = {}

        self._ctrl_recv, self._ctrl_send = self._create_control_con()

    def _create_control_con(self):
        if platform.system() == "Linux":
            return os.pipe()
        server = socket(AF_INET, SOCK_STREAM)
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
        return (res_list[0], clnt_sock)

    @handler("generate_events", priority=-9)
    def _on_generate_events(self, event):
        """
        Pollers have slightly higher priority than the default handler
        from Manager to ensure that they are invoked before the
        default handler. They act as event filters to avoid the additional
        invocation of the default handler which would be unnecessary
        overhead.
        """

        event.stop()
        self._generate_events(event)

    def resume(self):
        if isinstance(self._ctrl_send, socket):
            self._ctrl_send.send(b"\0")
        else:
            os.write(self._ctrl_send, b"\0")

    def _read_ctrl(self):
        try:
            if isinstance(self._ctrl_recv, socket):
                return self._ctrl_recv.recv(1)
            else:
                return os.read(self._ctrl_recv, 1)
        except (EnvironmentError, EOFError):
            return b"\0"

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
        if not (fd in self._read or fd in self._write) and fd in self._targets:
            del self._targets[fd]

    def removeWriter(self, fd):
        if fd in self._write:
            self._write.remove(fd)
        if not (fd in self._read or fd in self._write) and fd in self._targets:
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


class Select(BasePoller):

    """Select(...) -> new Select Poller Component

    Creates a new Select Poller Component that uses the select poller
    implementation. This poller is not recommended but is available for legacy
    reasons as most systems implement select-based polling for backwards
    compatibility.
    """

    channel = "select"

    def __init__(self, channel=channel):
        super(Select, self).__init__(channel=channel)

        self._read.append(self._ctrl_recv)

    def _preenDescriptors(self):
        for socks in (self._read[:], self._write[:]):
            for sock in socks:
                try:
                    select.select([sock], [sock], [sock], 0)
                except Exception:
                    self.discard(sock)

    def _generate_events(self, event):
        try:
            if not any([self._read, self._write]):
                return
            timeout = event.time_left
            if timeout < 0:
                r, w, _ = select.select(self._read, self._write, [])
            else:
                r, w, _ = select.select(self._read, self._write, [], timeout)
        except ValueError:
            # Possibly a file descriptor has gone negative?
            return self._preenDescriptors()
        except TypeError:
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

        for sock in w:
            if self.isWriting(sock):
                self.fire(_write(sock), self.getTarget(sock))

        for sock in r:
            if sock == self._ctrl_recv:
                self._read_ctrl()
                continue
            if self.isReading(sock):
                self.fire(_read(sock), self.getTarget(sock))


class Poll(BasePoller):

    """Poll(...) -> new Poll Poller Component

    Creates a new Poll Poller Component that uses the poll poller
    implementation.
    """

    channel = "poll"

    def __init__(self, channel=channel):
        super(Poll, self).__init__(channel=channel)

        self._map = {}
        self._poller = select.poll()

        self._disconnected_flag = (select.POLLHUP | select.POLLERR | select.POLLNVAL)

        self._read.append(self._ctrl_recv)
        self._updateRegistration(self._ctrl_recv)

    def _updateRegistration(self, fd):
        fileno = fd.fileno() if not isinstance(fd, int) else fd

        try:
            self._poller.unregister(fileno)
        except (KeyError, ValueError):
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
            try:
                del self._map[fileno]
            except KeyError:
                pass

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

    def _generate_events(self, event):
        try:
            timeout = event.time_left
            if timeout < 0:
                l = self._poller.poll()
            else:
                l = self._poller.poll(1000 * timeout)
        except SelectError as e:
            if e.args[0] == EINTR:
                return
            else:
                raise

        for fileno, event in l:
            self._process(fileno, event)

    def _process(self, fileno, event):
        if fileno not in self._map:
            return

        fd = self._map[fileno]
        if fd == self._ctrl_recv:
            self._read_ctrl()
            return

        if event & self._disconnected_flag and not (event & select.POLLIN):
            self.fire(_disconnect(fd), self.getTarget(fd))
            self._poller.unregister(fileno)
            super(Poll, self).discard(fd)
            del self._map[fileno]
        else:
            try:
                if event & select.POLLIN:
                    self.fire(_read(fd), self.getTarget(fd))
                if event & select.POLLOUT:
                    self.fire(_write(fd), self.getTarget(fd))
            except Exception as e:
                self.fire(_error(fd, e), self.getTarget(fd))
                self.fire(_disconnect(fd), self.getTarget(fd))
                self._poller.unregister(fileno)
                super(Poll, self).discard(fd)
                del self._map[fileno]


class EPoll(BasePoller):

    """EPoll(...) -> new EPoll Poller Component

    Creates a new EPoll Poller Component that uses the epoll poller
    implementation.
    """

    channel = "epoll"

    def __init__(self, channel=channel):
        super(EPoll, self).__init__(channel=channel)

        self._map = {}
        self._poller = select.epoll()

        self._disconnected_flag = (select.EPOLLHUP | select.EPOLLERR)

        self._read.append(self._ctrl_recv)
        self._updateRegistration(self._ctrl_recv)

    def _updateRegistration(self, fd):
        try:
            fileno = fd.fileno() if not isinstance(fd, int) else fd
            self._poller.unregister(fileno)
        except (SocketError, IOError, ValueError) as e:
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

    def _generate_events(self, event):
        try:
            timeout = event.time_left
            if timeout < 0:
                l = self._poller.poll()
            else:
                l = self._poller.poll(timeout)
        except IOError as e:
            if e.args[0] == EINTR:
                return
        except SelectError as e:
            if e.args[0] == EINTR:
                return
            else:
                raise

        for fileno, event in l:
            self._process(fileno, event)

    def _process(self, fileno, event):
        if fileno not in self._map:
            return

        fd = self._map[fileno]
        if fd == self._ctrl_recv:
            self._read_ctrl()
            return

        if event & self._disconnected_flag and not (event & select.POLLIN):
            self.fire(_disconnect(fd), self.getTarget(fd))
            self._poller.unregister(fileno)
            super(EPoll, self).discard(fd)
            del self._map[fileno]
        else:
            try:
                if event & select.EPOLLIN:
                    self.fire(_read(fd), self.getTarget(fd))
                if event & select.EPOLLOUT:
                    self.fire(_write(fd), self.getTarget(fd))
            except Exception as e:
                self.fire(_error(fd, e), self.getTarget(fd))
                self.fire(_disconnect(fd), self.getTarget(fd))
                self._poller.unregister(fileno)
                super(EPoll, self).discard(fd)
                del self._map[fileno]


class KQueue(BasePoller):

    """KQueue(...) -> new KQueue Poller Component

    Creates a new KQueue Poller Component that uses the kqueue poller
    implementation.
    """

    channel = "kqueue"

    def __init__(self, channel=channel):
        super(KQueue, self).__init__(channel=channel)
        self._map = {}
        self._poller = select.kqueue()

        self._read.append(self._ctrl_recv)
        self._map[self._ctrl_recv.fileno()] = self._ctrl_recv
        self._poller.control(
            [
                select.kevent(
                    self._ctrl_recv, select.KQ_FILTER_READ, select.KQ_EV_ADD
                )
            ], 0
        )

    def addReader(self, source, sock):
        super(KQueue, self).addReader(source, sock)
        self._map[sock.fileno()] = sock
        self._poller.control(
            [select.kevent(sock, select.KQ_FILTER_READ, select.KQ_EV_ADD)], 0
        )

    def addWriter(self, source, sock):
        super(KQueue, self).addWriter(source, sock)
        self._map[sock.fileno()] = sock
        self._poller.control(
            [select.kevent(sock, select.KQ_FILTER_WRITE, select.KQ_EV_ADD)], 0
        )

    def removeReader(self, sock):
        super(KQueue, self).removeReader(sock)
        self._poller.control(
            [
                select.kevent(sock, select.KQ_FILTER_READ, select.KQ_EV_DELETE)
            ],
            0
        )

    def removeWriter(self, sock):
        super(KQueue, self).removeWriter(sock)
        self._poller.control(
            [select.kevent(sock, select.KQ_FILTER_WRITE, select.KQ_EV_DELETE)],
            0
        )

    def discard(self, sock):
        super(KQueue, self).discard(sock)
        del self._map[sock.fileno()]
        self._poller.control(
            [
                select.kevent(
                    sock,
                    select.KQ_FILTER_WRITE | select.KQ_FILTER_READ,
                    select.KQ_EV_DELETE
                )
            ],
            0
        )

    def _generate_events(self, event):
        try:
            timeout = event.time_left
            if timeout < 0:
                l = self._poller.control(None, 1000)
            else:
                l = self._poller.control(None, 1000, timeout)
        except SelectError as e:
            if e[0] == EINTR:
                return
            else:
                raise

        for event in l:
            self._process(event)

    def _process(self, event):
        if event.ident not in self._map:
            # shouldn't happen ?
            # we unregister the socket since we don't care about it anymore
            self._poller.control(
                [
                    select.kevent(
                        event.ident, event.filter, select.KQ_EV_DELETE
                    )
                ],
                0
            )

            return

        sock = self._map[event.ident]
        if sock == self._ctrl_recv:
            self._read_ctrl()
            return

        if event.flags & select.KQ_EV_ERROR:
            self.fire(_error(sock, "error"), self.getTarget(sock))
        elif event.flags & select.KQ_EV_EOF:
            self.fire(_disconnect(sock), self.getTarget(sock))
        elif event.filter == select.KQ_FILTER_WRITE:
            self.fire(_write(sock), self.getTarget(sock))
        elif event.filter == select.KQ_FILTER_READ:
            self.fire(_read(sock), self.getTarget(sock))


Poller = Select

__all__ = ("BasePoller", "Poller", "Select", "Poll", "EPoll", "KQueue")
