# Module:   io
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""File I/O Components

This module implements an Asynchronous File Component that is a wrapper
around the standard file object where read/write operations are
non-blocking. Three additional convenient components are also provided,
namely Stdin, Stdout and Stderr.
"""

import os
import fcntl
import errno
import select
from collections import deque

from circuits import Event, Component


POLL_INTERVAL = 0.00001
BUFFER_SIZE = 131072


class Opened(Event): pass
class Closed(Event): pass
class Read(Event): pass
class Write(Event): pass
class Error(Event): pass


class _File(file):

    def setblocking(self, flag):
        " set/clear blocking mode"
        # get the file descriptor
        fd = self.fileno()
        # get the file's current flag settings
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        if flag:
            # clear non-blocking mode from flags
            fl = fl & ~os.O_NONBLOCK
        else:
            # set non-blocking mode from flags
            fl = fl | os.O_NONBLOCK
        # update the file's flags
        fcntl.fcntl(fd, fcntl.F_SETFL, fl)

    def write(self, data):
        try:
            return os.write(self.fileno(), data)
        except OSError, e:
            raise IOError(e.errno, e.strerror, e.filename)


class File(Component):

    channel = "file"

    def __init__(self, filename, mode, channel=channel):
        super(File, self).__init__(channel=channel)

        self.name = filename
        self.mode = mode

        self._read = []
        self._write = []
        self._buffer = deque()

        self._fd = _File(self.name, self.mode)
        self._fd.setblocking(False)
        self._read.append(self._fd)

        self.push(Opened(self.name), "opened")

    @property
    def closed(self):
        return self._fd.closed if hasattr(self, "_fd") else None

    def __tick__(self):
        self.poll()

    def poll(self, wait=POLL_INTERVAL):
        if not self.closed:
            try:
                r, w, e = select.select(self._read, self._write, [], wait)
            except select.error, error:
                if error[0] == 4:
                    pass
                else:
                    self.push(Error(error), "error")
                    return

            if w:
                data = self._buffer.popleft()
                self._fd.write(data)
                if not self._buffer:
                    self._write.remove(self._fd)

            if r:
                try:
                    data = self._fd.read(BUFFER_SIZE)
                except IOError, e:
                    if e[0] == errno.EBADF:
                        data = None

                if data:
                    self.push(Read(data), "read")

    def write(self, data):
        if self._fd not in self._write:
            self._write.append(self._fd)
        self._buffer.append(data)

    def close(self):
        self._fd.close()
        self._read = []
        self._write = []
        self.push(Closed(self.name), "closed")

class StdIn(File):

    channel = "stdin"

    def __init__(self, channel=channel):
        super(StdIn, self).__init__("/dev/stdin", "r", channel=channel)

stdin = StdIn()

class StdOut(File):

    channel = "stdout"

    def __init__(self, channel=channel):
        super(StdOut, self).__init__("/dev/stdout", "w", channel=channel)

stdout = StdOut()

class StdErr(File):

    channel = "stderr"

    def __init__(self, channel=channel):
        super(StdErr, self).__init__("/dev/stderr", "w", channel=channel)

stderr = StdErr()
