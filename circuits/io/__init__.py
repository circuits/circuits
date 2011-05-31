# Module:   io
# Date:     4th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""I/O Components

This package contains various I/O Components. Provided are a a generic File
Component, StdIn, StdOut and StdErr components. Instances of StdIn, StdOUt
and StdErr are also created by importing this package.
"""

import os
import sys
import errno
import select
from collections import deque

from circuits.tools import tryimport
from circuits.core import Event, Component

fcntl = tryimport("fcntl")
serial = tryimport("serial")

TIMEOUT = 0.2
BUFSIZE = 4096


class EOF(Event):
    """EOF Event"""


class Seek(Event):
    """Seek Event"""


class Read(Event):
    """Read Event"""


class Close(Event):
    """Close Event"""


class Write(Event):
    """Write Event"""


class Error(Event):
    """Error Event"""


class Opened(Event):
    """Opened Event"""


class Closed(Event):
    """Closed Event"""


class File(Component):

    channel = "file"

    def __init__(self, filename=None, mode="r", fd=None, autoclose=True,
            bufsize=BUFSIZE, encoding="utf-8", channel=channel):
        super(File, self).__init__(channel=channel)

        self.bufsize = bufsize
        self.encoding = encoding
        self.autoclose = autoclose

        if filename is not None:
            self.mode = mode
            self.filename = filename
            self._fd = open(filename, mode)
        else:
            self._fd = fd
            self.mode = fd.mode
            self.filename = fd.name

        if fcntl is not None:
            # Set non-blocking file descriptor (non-portable)
            flag = fcntl.fcntl(self._fd, fcntl.F_GETFL)
            flag = flag | os.O_NONBLOCK
            fcntl.fcntl(self._fd, fcntl.F_SETFL, flag)

        self._read = []
        self._write = []
        self._buffer = deque()

        if any([m for m in "r+" if m in self._fd.mode]):
            self._read.append(self._fd)

        self.fire(Opened(self.filename))

    @property
    def closed(self):
        return self._fd.closed if hasattr(self, "_fd") else None

    def __tick__(self, wait=TIMEOUT):
        if not self.closed:
            try:
                r, w, e = select.select(self._read, self._write, [], wait)
            except select.error as error:
                if not error[0] == errno.EINTR:
                    self.fire(Error(error))
                return

            if w and self._buffer:
                data = self._buffer.popleft()
                try:
                    if isinstance(data, str):
                        data = data.encode(self.encoding)
                    bytes = os.write(self._fd.fileno(), data)
                    if bytes < len(data):
                        self._buffer.append(data[bytes:])
                    elif not self._buffer:
                        self._write.remove(self._fd)
                except OSError as error:
                    self.fire(Error(error))

            if r:
                try:
                    data = os.read(self._fd.fileno(), self.bufsize)
                except IOError as e:
                    if e[0] == errno.EBADF:
                        data = None

                if data:
                    self.fire(Read(data))
                elif self.autoclose:
                    self.fire(EOF())
                    self.close()

    def write(self, data):
        if self._fd not in self._write:
            self._write.append(self._fd)
        self._buffer.append(data)

    def close(self):
        self._fd.close()
        self._read = []
        self._write = []
        self.fire(Closed(self.filename))

    def seek(self, offset, whence=0):
        self._fd.seek(offset, whence)


class Serial(Component):

    channel = "serial"

    def __init__(self, port, baudrate=115200, bufsize=BUFSIZE,
            timeout=TIMEOUT, channel=channel):
        super(Serial, self).__init__(channel=channel)

        if serial is None:
            raise RuntimeError("No serial support available")

        self.port = port
        self.baudrate = baudrate

        self._serial = serial.Serial()
        self._serial.port = port
        self._serial.baudrate = baudrate

        if os.name == "posix":
            self._serial.timeout = 0  # non-blocking (POSIX)
        else:
            self._serial.timeout = timeout

        self._buffer = deque()
        self._bufsize = bufsize
        self._timeout = timeout

        self._read = []
        self._write = []

        self._serial.open()
        self._fd = self._serial.fileno()

        self._read.append(self._fd)

        self.fire(Opened(self.port))

    def __tick__(self):
        r, w, e = select.select(self._read, self._write, [], self._timeout)

        if w and self._buffer:
            data = self._buffer.popleft()
            try:
                bytes = os.write(self._fd, data)
                if bytes < len(data):
                    self._buffer.append(data[bytes:])
                else:
                    if not self._buffer and self._fd in self._write:
                        self._write.remove(self._fd)
            except OSError as error:
                self.fire(Error(error))

        if r:
            data = os.read(self._fd, self._bufsize)
            if data:
                self.fire(Read(data))

    def write(self, data):
        if self._fd not in self._write:
            self._write.append(self._fd)
        self._buffer.append(data)

    def close(self):
        self._fd = None
        self._read = []
        self._write = []
        self._serial.close()
        self.fire(Closed(self.port))

try:
    stdin = File(fd=sys.stdin, mode="r", channel="stdin")
    stdout = File(fd=sys.stdout, mode="w", channel="stdout")
    stderr = File(fd=sys.stderr, mode="w", channel="stderr")
except:
    pass
