# Module:   io
# Date:     4th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""I/O Components

This package contains various I/O Components. Provided are a a generic File
Component, StdIn, StdOut and StdErr components. Instances of StdIn, StdOUt
and StdErr are also created by importing this package.
"""

import os
import fcntl
import errno
import select
from collections import deque

from circuits.core import Event, Component

TIMEOUT = 0.00001
BUFSIZE = 131072

class EOF(Event): pass
class Read(Event): pass
class Write(Event): pass
class Error(Event): pass
class Opened(Event): pass
class Closed(Event): pass

def setblocking(fd, flag):
    """Set/Clear blocking mode of a file descriptor"""

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

class File(Component):

    channel = "file"

    def __init__(self, *args, **kwargs):
        channel = kwargs.get("channel", File.channel)
        super(File, self).__init__(channel=channel)

        if len(args) == 1 and type(args[0]) == file:
            self._fd = args[0]
        else:
            self._fd = open(*args)

        self.filename = self._fd.name
        self.mode = self._fd.mode

        setblocking(self._fd, False)

        self._read = []
        self._write = []
        self._buffer = deque()

        self._read.append(self._fd)

        self.push(Opened(self.filename), "opened")

    @property
    def closed(self):
        return self._fd.closed if hasattr(self, "_fd") else None

    def __tick__(self, wait=TIMEOUT):
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
                try:
                    bytes = os.write(self._fd.fileno(), data)
                    if bytes < len(data):
                        self._buffer.append(data[bytes:])
                    elif not self._buffer:
                        self._write.remove(self._fd)
                except OSError, error:
                    self.push(Error(error), "error")

            if r:
                try:
                    data = os.read(self._fd.fileno(), BUFSIZE)
                except IOError, e:
                    if e[0] == errno.EBADF:
                        data = None

                if data:
                    self.push(Read(data), "read")
                else:
                    self.push(EOF(), "eof")
                    self.close()

    def write(self, data):
        if self._fd not in self._write:
            self._write.append(self._fd)
        self._buffer.append(data)

    def close(self):
        self._fd.close()
        self._read = []
        self._write = []
        self.push(Closed(self.filename), "closed")

    def seek(self, offset, whence=0):
        self._fd.seek(offset, whence)

class StdIn(File):

    channel = "stdin"

    def __init__(self, channel=channel):
        super(StdIn, self).__init__("/dev/stdin", "r", channel=channel)

class StdOut(File):

    channel = "stdout"

    def __init__(self, channel=channel):
        super(StdOut, self).__init__("/dev/stdout", "w", channel=channel)

class StdErr(File):

    channel = "stderr"

    def __init__(self, channel=channel):
        super(StdErr, self).__init__("/dev/stderr", "w", channel=channel)

stdin = StdIn()
stdout = StdOut()
stderr = StdErr()
