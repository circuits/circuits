# Module:   io
# Date:     4th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""I/O Components

This package contains various I/O Components. Provided are a a generic File
Component, StdIn, StdOut and StdErr components. Instances of StdIn, StdOUt
and StdErr are also created by importing this package.
"""

import sys
import os
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False
import errno
import select
from collections import deque

try:
    import serial
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

from circuits.core import Event, Component

TIMEOUT = 0.2
BUFSIZE = 4096

class EOF(Event): pass
class Seek(Event): pass
class Read(Event): pass
class Close(Event): pass
class Write(Event): pass
class Error(Event): pass
class Opened(Event): pass
class Closed(Event): pass

class File(Component):

    def __init__(self, *args, **kwargs):
        channel = kwargs.get("channel", File.channel)
        super(File, self).__init__(channel=channel)

        self.autoclose = kwargs.get("autoclose", True)
        self.encoding = kwargs.get("encoding", "utf-8")

        if len(args) == 1 and isinstance(args[0], file) or args[0] in (sys.stdin, sys.stdout, sys.stderr):
            self._fd = args[0]
        else:
            self._fd = open(*args)

        self.filename = self._fd.name
        self.mode = self._fd.mode

        self.bufsize = kwargs.get("bufsize", BUFSIZE)

        if HAS_FCNTL:
            # Set non-blocking file descriptor (non-portable)
            flag = fcntl.fcntl(self._fd, fcntl.F_GETFL)
            flag = flag | os.O_NONBLOCK
            fcntl.fcntl(self._fd, fcntl.F_SETFL, flag)

        self._read = []
        self._write = []
        self._buffer = deque()

        if any(filter(lambda m: m in self._fd.mode, "r+")):
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
                if not error[0] == errno.EINTR:
                    self.push(Error(error), "error")
                return

            if w and self._buffer:
                data = self._buffer.popleft()
                try:
                    if type(data) is unicode:
                        data = data.encode(self.encoding)
                    bytes = os.write(self._fd.fileno(), data)
                    if bytes < len(data):
                        self._buffer.append(data[bytes:])
                    elif not self._buffer:
                        self._write.remove(self._fd)
                except OSError, error:
                    self.push(Error(error), "error")

            if r:
                try:
                    data = os.read(self._fd.fileno(), self.bufsize)
                except IOError, e:
                    if e[0] == errno.EBADF:
                        data = None

                if data:
                    self.push(Read(data), "read")
                elif self.autoclose:
                    self.push(EOF())
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

if HAS_SERIAL:

    class Serial(Component):

        def __init__(self, port, **kwargs):
            channel = kwargs.get("channel", Serial.channel)
            super(Serial, self).__init__(channel=channel)

            self.port = port

            self._serial = serial.Serial()
            self._serial.port = port
            self._serial.baudrate = kwargs.get("baudrate", 115200)

            if os.name == "posix":
                self._serial.timeout = 0 # non-blocking (POSIX)
            else:
                self._serial.timeout = kwargs.get("timeout", TIMEOUT)

            self._buffer = deque()
            self._bufsize = kwargs.get("bufsize", BUFSIZE)
            self._timeout = kwargs.get("timeout", TIMEOUT)

            self._read = []
            self._write = []

            self._serial.open()
            self._fd = self._serial.fileno()

            self._read.append(self._fd)

            self.push(Opened(self.port))

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
                except OSError, error:
                    self.push(Error(error))

            if r:
                data = os.read(self._fd, self._bufsize)
                if data:
                    self.push(Read(data))

        def write(self, data):
            if self._fd not in self._write:
                self._write.append(self._fd)
            self._buffer.append(data)

        def close(self):
            self._fd = None
            self._read = []
            self._write = []
            self._serial.close()
            self.push(Closed(self.port))

try:
    stdin = File(sys.stdin, "r", channel="stdin")
    stdout = File(sys.stdout, "w", channel="stdout")
    stderr = File(sys.stderr, "w", channel="stderr")
except:
    pass
